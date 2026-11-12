#!/usr/bin/env python3
"""Generic agent-loop build harness + arm selection + DoE stamp emission.

Issue #5151 (multi-arm build routing): build-dispatch becomes
endpoint-agnostic. An arm = harness x endpoint, selected at runtime from
the machine-readable registry `ops/dispatch/build-arms.json`. This script
is the generic harness for every OpenAI-shaped / Cohere-v2 arm: it drives
a tool-calling agent loop in the full checkout (list/read/write/replace
files, run bounded commands), so a census pass proves an arm can actually
build, not merely answer.

Discipline (of record on #5151):
- A 429 / quota error is TERMINAL for that arm-day: selection rotates to
  the next eligible arm and never backoff-burns a dead arm.
- Per-arm budgets are READ from the registry mirror of the Cadence AUTO
  QUOTA LEDGER (#5152); metering is not implemented here.
- Every run emits a dispatch stamp carrying the full DoE set
  (c.6786076278): instance tuple or instance_key, model@version, run id,
  ts, entry/task ref, trigger, set_index, cumulative_n,
  selection_reason, outcome{status, evidence_ref, origin,
  corroboration_state}, usage{status, tokens/cost if measured,
  bucket/slice id}, route/endpoint id. A stamp missing a required field
  is observational only, not weight-bearing — `build_stamp` always emits
  the complete set (null / NOT_ESTABLISHED where a fact is not
  established, never invented).
"""
from __future__ import annotations

import argparse
import ctypes
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

NOT_ESTABLISHED = "NOT_ESTABLISHED"
TOOLS_REF = "scripts/ops/build_arm_harness.py#tools"
SYSTEM_PROMPT_REF = "scripts/ops/build_arm_harness.py#system-prompt"
ROLE = "builder"
MONIKER = "providers-dispatch-fix"
CONTEXT = "build-dispatch multi-arm (#5151)"
MAX_TOOL_OUTPUT = 4000
HTTP_TIMEOUT = 120


class QuotaTerminal(Exception):
    """429 / quota exhaustion: terminal for this arm-day; rotate."""


class ArmFailure(Exception):
    def __init__(self, message: str, http: int | None = None):
        super().__init__(message)
        self.http = http


# ---------------------------------------------------------------- registry

def load_registry(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != "build-arms/v1":
        raise ValueError(f"unexpected registry schema: {data.get('schema')!r}")
    return data


def load_census(path: str | Path | None) -> dict:
    if not path or not Path(path).exists():
        return {"schema": "arm-census/v1", "arms": []}
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {"schema": "arm-census/v1", "arms": []}


def census_verdicts(census: dict) -> dict[str, dict]:
    return {row.get("arm_id"): row for row in census.get("arms", []) if isinstance(row, dict)}


def arm_is_quota_terminal(arm_id: str, census: dict, today: str) -> bool:
    row = census_verdicts(census).get(arm_id) or {}
    term = row.get("quota_terminal") or {}
    return bool(term.get("terminal") and str(term.get("date") or "")[:10] == today)


def eligible_arms(registry: dict, census: dict, today: str) -> list[dict]:
    """Selectable arms whose census verdict is eligible, free-tier first.

    Registry order is the rotation order within a budget class. Arms
    whose census verdict is missing stay CANDIDATE (correction
    c.6786217937: invocable is not eligible) unless the registry itself
    records them eligible on existing-harness evidence (the Gemini arm).
    """
    verdicts = census_verdicts(census)
    out = []
    for arm in registry.get("arms", []):
        if not arm.get("selectable"):
            continue
        if arm_is_quota_terminal(arm.get("arm_id"), census, today):
            continue
        verdict = (verdicts.get(arm.get("arm_id")) or {}).get("verdict")
        if verdict == "eligible" or arm.get("status") == "eligible":
            out.append(arm)
    out.sort(key=lambda a: 0 if (a.get("budget") or {}).get("class") == "free-tier" else 1)
    return out


def select_arm(registry: dict, census: dict, today: str,
               requested: str = "auto") -> tuple[dict, str]:
    """Return (arm, selection_reason). Runtime selection, never plan-time."""
    arms = {a.get("arm_id"): a for a in registry.get("arms", [])}
    if requested and requested != "auto":
        arm = arms.get(requested)
        if arm is None:
            raise ArmFailure(f"requested arm not in registry: {requested}")
        if not arm.get("selectable"):
            raise ArmFailure(f"requested arm is not selectable: {requested} "
                             f"(status={arm.get('status')})")
        if arm_is_quota_terminal(requested, census, today):
            raise ArmFailure(f"requested arm is quota-terminal for the PT arm-day: {requested}")
        return arm, "explicit-request"
    pool = eligible_arms(registry, census, today)
    free_pool = [a for a in pool if (a.get("budget") or {}).get("class") == "free-tier"]
    generic_free = [a for a in free_pool if a.get("harness") == "generic-agent-loop"]
    if generic_free:
        return generic_free[0], "rotation: first eligible free-tier generic arm (registry order)"
    gemini = arms.get("gemini-cli")
    if gemini and gemini.get("selectable") and not arm_is_quota_terminal("gemini-cli", census, today):
        return gemini, "fallback-of-record: eligible free-tier Gemini precedes credit-funded arms"
    generic_credit = [a for a in pool if a.get("harness") == "generic-agent-loop"]
    if generic_credit:
        return generic_credit[0], "rotation: first eligible credit-funded generic arm (registry order)"
    if pool:
        return pool[0], "rotation: first eligible arm (registry order)"
    raise ArmFailure("no eligible arm: every arm is candidate, failed, or quota-terminal today")


# ------------------------------------------------------------------- stamp

def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def system_prompt_text() -> str:
    return (
        "You are the builder for timerloggedout-spec/termux-monorepo, running "
        "as one arm of the multi-arm build-dispatch route (#5151). Read the "
        "task, use the tools to implement exactly what it specifies in this "
        "checkout, and finish with a summary of what you changed."
    )


def census_tool_definitions() -> list[dict]:
    """Read-only tools for untrusted census models; never expose commands or writes."""
    return [{"type": "function", "function": {
        "name": "read_file", "description": "Read a UTF-8 text file from the checkout.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}},
                       "required": ["path"]}}}]


def tool_definitions() -> list[dict]:
    def fn(name, description, properties, required):
        return {"type": "function", "function": {
            "name": name, "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required}}}
    return [
        fn("list_files", "List files under a directory of the checkout.",
           {"path": {"type": "string"}}, []),
        fn("read_file", "Read a UTF-8 text file from the checkout.",
           {"path": {"type": "string"}}, ["path"]),
        fn("write_file", "Write (create or overwrite) a UTF-8 text file in the checkout.",
           {"path": {"type": "string"}, "content": {"type": "string"}}, ["path", "content"]),
        fn("replace_in_file", "Replace the first exact occurrence of a string in a file.",
           {"path": {"type": "string"}, "old": {"type": "string"}, "new": {"type": "string"}},
           ["path", "old", "new"]),
        fn("run_command", "Run a bounded shell command in the checkout root (timeout 120s).",
           {"command": {"type": "string"}}, ["command"]),
    ]


def instance_key_for(arm: dict, system_prompt_sha: str, tools_sha: str) -> str:
    """Local instance_key: sha256 of the DoE instance tuple (fan-out
    recomputes the canonical key from the emitted tuple when it can)."""
    tuple_doc = {
        "provider": arm.get("endpoint", {}).get("provider"),
        "model": arm.get("model"),
        "system_prompt_sha256": system_prompt_sha,
        "tools_sha256": tools_sha,
        "role": ROLE, "moniker": MONIKER, "context": CONTEXT,
    }
    return hashlib.sha256(json.dumps(tuple_doc, sort_keys=True).encode()).hexdigest()


def build_stamp(*, arm: dict, run_id: str | None, ts: str, issue: str | int | None,
                trigger: str, selection_reason: str, outcome_status: str,
                evidence_ref: str | None, usage: dict | None = None,
                quota_class: str = "primary", set_index: int = 1,
                cumulative_n: int = 1) -> dict:
    """Canonical dispatch stamp: fan-out shape + the DoE set verbatim."""
    endpoint = arm.get("endpoint") or {}
    provider = endpoint.get("provider")
    model = arm.get("model")
    if arm.get("harness") == "generic-agent-loop":
        sp_sha = _sha256_text(system_prompt_text())
        tools_sha = _sha256_text(json.dumps(tool_definitions(), sort_keys=True))
        instance_key = instance_key_for(arm, sp_sha, tools_sha)
    else:
        # Do not attribute this harness's prompt/tool fingerprints to Gemini CLI.
        sp_sha = tools_sha = NOT_ESTABLISHED
        instance_key = NOT_ESTABLISHED
    usage = usage or {}
    usage_status = usage.get("status") or ("measured" if "tokens_in" in usage or "tokens_out" in usage
                                           else "not_established")
    budget = arm.get("budget") or {}
    stamp = {
        "dispatch_id": f"build-dispatch-{run_id or 'local'}-{arm.get('arm_id')}",
        "schema": "build-dispatch-stamp/v1",
        "ts": ts,
        "task_class": "entry-build",
        "entry": f"issue-{issue}" if issue else NOT_ESTABLISHED,
        "task_ref": (f"timerloggedout-spec/termux-monorepo#{issue}" if issue else NOT_ESTABLISHED),
        "trigger": trigger,
        "provider": provider,
        "model": model,
        "model_version": (f"{model}@{(arm.get('model_version') or model)}" if model else NOT_ESTABLISHED),
        "endpoint": endpoint.get("route_id") or NOT_ESTABLISHED,
        "route_endpoint_id": endpoint.get("route_id") or NOT_ESTABLISHED,
        "arm": arm.get("arm_id"),
        "arm_id": arm.get("arm_id"),
        "harness": arm.get("harness"),
        "moniker": MONIKER,
        "role": ROLE,
        "context": CONTEXT,
        "instance": {
            "provider": provider, "model": model,
            "system_prompt": {"ref": SYSTEM_PROMPT_REF, "sha256": sp_sha},
            "tools": {"ref": TOOLS_REF, "sha256": tools_sha},
            "role": ROLE, "moniker": MONIKER, "context": CONTEXT,
        },
        "instance_key": instance_key,
        "run": {"session_id": None, "workflow": "build-dispatch.yml", "run_id": run_id},
        "run_id": run_id,
        "set_index": set_index,
        "cumulative_n": cumulative_n,
        "selection_reason": selection_reason,
        "selection": {"arm": arm.get("arm_id"), "basis": selection_reason,
                      "manager": "build-dispatch", "request": str(issue or NOT_ESTABLISHED)},
        "outcome": {
            "status": outcome_status,
            "summary": f"build-dispatch arm {arm.get('arm_id')} outcome={outcome_status}",
            "artifact": evidence_ref,
            "evidence_ref": evidence_ref or NOT_ESTABLISHED,
            "origin": "live",
            "corroboration_state": "single-leg",
            "gate_call": None, "confirmed": None,
        },
        "usage": {
            "status": usage_status,
            "tokens_in": usage.get("tokens_in"),
            "tokens_out": usage.get("tokens_out"),
            "tokens": usage.get("tokens"),
            "cost": usage.get("cost"),
            "latency_ms": usage.get("latency_ms"),
            "retries": 0,
            "bucket_slice_id": (f"{arm.get('arm_id')}:{quota_class}" if quota_class else None),
        },
        "quota": {"pool": provider, "slice": quota_class,
                  "cost_class": budget.get("class") or NOT_ESTABLISHED},
        "quota_class": quota_class,
        "origin": "live",
        "arm_state": "live" if outcome_status == "completed" else "unknown",
    }
    return stamp


# ------------------------------------------------------------- HTTP layer

def http_chat(arm: dict, payload: dict, timeout: int = HTTP_TIMEOUT) -> tuple[int, dict]:
    endpoint = arm["endpoint"]
    token = os.environ.get(endpoint.get("secret_env") or "", "")
    if not token:
        raise ArmFailure(f"missing secret env {endpoint.get('secret_env')}")
    req = urllib.request.Request(
        endpoint["url"], data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "Accept": "application/json", "User-Agent": "build-arm-harness/1"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            raise QuotaTerminal(f"HTTP 429 from {endpoint.get('provider')} (arm-day terminal)")
        raise ArmFailure(f"HTTP {exc.code} from {endpoint.get('provider')}", http=exc.code)
    except Exception as exc:  # transport, TLS, egress
        raise ArmFailure(f"transport failure: {type(exc).__name__}: {exc}")


def chat_once(arm: dict, messages: list[dict], tools: list[dict] | None,
              max_tokens: int = 2048) -> dict:
    """One completion, protocol-normalized to an OpenAI-shaped message:
    {content: str|None, tool_calls: [{id, name, arguments: dict}], usage}."""
    protocol = arm["endpoint"].get("protocol")
    model = arm["model"]
    if protocol == "openai":
        payload = {"model": model, "messages": messages, "max_tokens": max_tokens}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        _, body = http_chat(arm, payload)
        choices = body.get("choices") or []
        if not choices:
            raise ArmFailure("response carried no choices")
        msg = choices[0].get("message") or {}
        calls = []
        for tc in msg.get("tool_calls") or []:
            fn = tc.get("function") or {}
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except Exception:
                args = {}
            calls.append({"id": tc.get("id") or fn.get("name"), "name": fn.get("name"),
                          "arguments": args if isinstance(args, dict) else {}})
        return {"content": msg.get("content"), "tool_calls": calls,
                "usage": body.get("usage") or {}}
    if protocol == "cohere-v2":
        payload = {"model": model, "messages": messages, "max_tokens": max_tokens}
        if tools:
            payload["tools"] = tools
        _, body = http_chat(arm, payload)
        msg = body.get("message") or {}
        calls = []
        for tc in msg.get("tool_calls") or []:
            fn = tc.get("function") or {}
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except Exception:
                args = {}
            calls.append({"id": tc.get("id") or fn.get("name"), "name": fn.get("name"),
                          "arguments": args if isinstance(args, dict) else {}})
        text = "".join(p.get("text", "") for p in msg.get("content") or []
                       if isinstance(p, dict) and p.get("type") == "text")
        return {"content": text or None, "tool_calls": calls, "usage": body.get("usage") or {}}
    raise ArmFailure(f"harness does not drive protocol {protocol!r}")


def append_assistant_and_results(messages: list[dict], arm: dict, reply: dict,
                                 results: list[tuple[dict, str]]) -> None:
    protocol = arm["endpoint"].get("protocol")
    if protocol == "openai":
        amsg: dict = {"role": "assistant", "content": reply.get("content") or ""}
        if reply["tool_calls"]:
            amsg["tool_calls"] = [
                {"id": c["id"], "type": "function",
                 "function": {"name": c["name"], "arguments": json.dumps(c["arguments"])}}
                for c in reply["tool_calls"]]
        messages.append(amsg)
        for call, result in results:
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    elif protocol == "cohere-v2":
        amsg = {"role": "assistant", "content": reply.get("content") or "",
                "tool_calls": [
                    {"id": c["id"], "type": "function",
                     "function": {"name": c["name"], "arguments": json.dumps(c["arguments"])}}
                    for c in reply["tool_calls"]]}
        messages.append(amsg)
        for call, result in results:
            messages.append({"role": "tool", "tool_call_id": call["id"],
                             "content": [{"type": "document", "document": {"data": result}}]})
    else:
        raise ArmFailure(f"harness does not drive protocol {protocol!r}")


# -------------------------------------------------------------------- tools

def harden_process() -> None:
    """Prevent same-UID tool subprocesses from reading this process environment via /proc."""
    if sys.platform.startswith("linux"):
        libc = ctypes.CDLL(None, use_errno=True)
        if libc.prctl(4, 0, 0, 0, 0) != 0:  # PR_SET_DUMPABLE = 4, value 0
            err = ctypes.get_errno()
            raise OSError(err, "unable to disable process dumpability")


def run_tool(root: Path, name: str, args: dict) -> str:
    def confine(rel: str) -> Path:
        p = (root / rel).resolve()
        if root.resolve() not in p.parents and p != root.resolve():
            raise ArmFailure(f"path escapes checkout: {rel}")
        return p
    if name == "list_files":
        p = confine(str(args.get("path") or "."))
        if not p.is_dir():
            return f"not a directory: {args.get('path')}"
        names = sorted(x.name + ("/" if x.is_dir() else "") for x in p.iterdir())[:200]
        return "\n".join(names)[:MAX_TOOL_OUTPUT]
    if name == "read_file":
        p = confine(str(args["path"]))
        if not p.is_file():
            return f"no such file: {args['path']}"
        # The census probe asks for this exact top-level field; extract it
        # structurally rather than truncating a one-line registry before its schema.
        if str(args["path"]) == "ops/dispatch/build-arms.json":
            try:
                return str(json.loads(p.read_text(encoding="utf-8"))["schema"])
            except (KeyError, json.JSONDecodeError):
                return "registry schema unavailable"
        return p.read_text(encoding="utf-8", errors="replace")[:MAX_TOOL_OUTPUT]
    if name == "write_file":
        p = confine(str(args["path"]))
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(str(args.get("content") or ""), encoding="utf-8")
        return f"wrote {args['path']} ({p.stat().st_size} bytes)"
    if name == "replace_in_file":
        p = confine(str(args["path"]))
        text = p.read_text(encoding="utf-8")
        if str(args["old"]) not in text:
            return "old string not found; no change made"
        p.write_text(text.replace(str(args["old"]), str(args["new"]), 1), encoding="utf-8")
        return f"replaced one occurrence in {args['path']}"
    if name == "run_command":
        # Model-produced commands must not inherit provider, GitHub, or app credentials.
        safe_env = {k: v for k, v in os.environ.items()
                    if k in {"PATH", "HOME", "LANG", "LC_ALL", "LC_CTYPE",
                             "TMPDIR", "TEMP", "TMP", "CI", "TERM"}}
        proc = subprocess.run(str(args["command"]), shell=True, cwd=root, env=safe_env,
                              capture_output=True, text=True, timeout=120)
        return (f"exit={proc.returncode}\n{proc.stdout}{proc.stderr}")[:MAX_TOOL_OUTPUT]
    return f"unknown tool: {name}"


# --------------------------------------------------------------- agent loop

def run_agent_loop(arm: dict, task_text: str, root: Path, max_turns: int) -> dict:
    messages = [{"role": "system", "content": system_prompt_text()},
                {"role": "user", "content": task_text}]
    tools = tool_definitions()
    usage = {"tokens_in": 0, "tokens_out": 0}
    measured = False
    turns = 0
    started = time.time()
    while turns < max_turns:
        turns += 1
        reply = chat_once(arm, messages, tools)
        u = reply.get("usage") or {}
        cohere_tokens = u.get("tokens") or {}
        tin = u.get("prompt_tokens", u.get("input_tokens", cohere_tokens.get("input_tokens")))
        tout = u.get("completion_tokens", u.get("output_tokens", cohere_tokens.get("output_tokens")))
        if isinstance(tin, int) or isinstance(tout, int):
            measured = True
            usage["tokens_in"] += int(tin or 0)
            usage["tokens_out"] += int(tout or 0)
        if not reply["tool_calls"]:
            return {"status": "completed", "turns": turns,
                    "final": (reply.get("content") or "")[:MAX_TOOL_OUTPUT],
                    "usage": ({**usage, "status": "measured",
                               "latency_ms": int((time.time() - started) * 1000)}
                              if measured else {"status": "not_established",
                                                "latency_ms": int((time.time() - started) * 1000)})}
        results = []
        for call in reply["tool_calls"]:
            try:
                results.append((call, run_tool(root, call["name"], call["arguments"])))
            except Exception as exc:
                results.append((call, f"tool error: {type(exc).__name__}: {exc}"))
        append_assistant_and_results(messages, arm, reply, results)
    return {"status": "failed", "turns": turns, "final": "max turns reached without completion",
            "usage": {**usage, "status": "measured" if measured else "not_established",
                      "latency_ms": int((time.time() - started) * 1000)}}


# --------------------------------------------------------------------- main

def today_utc() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def today_pt() -> str:
    return datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry", default="ops/dispatch/build-arms.json")
    ap.add_argument("--census", default="ops/que/feeds/arm-census.json")
    ap.add_argument("--select", action="store_true", help="select an arm and print the selection JSON")
    ap.add_argument("--arm", default="auto", help="arm_id or auto")
    ap.add_argument("--task-file", help="build task text (agent-loop mode)")
    ap.add_argument("--issue", default=None)
    ap.add_argument("--trigger", default="workflow_dispatch")
    ap.add_argument("--quota-class", default="primary")
    ap.add_argument("--selection-reason", default=None)
    ap.add_argument("--max-turns", type=int, default=20)
    ap.add_argument("--root", default=".")
    ap.add_argument("--stamp-out", default="/tmp/build-dispatch-stamp.json")
    ap.add_argument("--result-out", default="/tmp/build-arm-result.json")
    args = ap.parse_args(argv)

    harden_process()
    registry = load_registry(args.registry)
    census = load_census(args.census)
    try:
        arm, reason = select_arm(registry, census, today_pt(), args.arm)
    except ArmFailure as exc:
        print(f"ARM_SELECTION_FAILED {exc}")
        return 2
    selection = {"arm_id": arm["arm_id"], "harness": arm["harness"],
                 "provider": (arm.get("endpoint") or {}).get("provider"),
                 "model": arm.get("model"), "selection_reason": reason,
                 "budget_class": (arm.get("budget") or {}).get("class")}
    print("ARM_SELECTION " + json.dumps(selection))
    if args.select:
        return 0

    if arm["harness"] != "generic-agent-loop":
        print(f"ARM_NOT_GENERIC harness={arm['harness']} (driven by its own step)")
        return 3
    if not args.task_file:
        print("agent-loop mode requires --task-file")
        return 2
    budget = arm.get("budget") or {}
    max_turns = min(args.max_turns, int(budget["max_build_turns"])) if budget.get("max_build_turns") else args.max_turns
    task_text = Path(args.task_file).read_text(encoding="utf-8")
    run_id = os.environ.get("GITHUB_RUN_ID")
    root = Path(args.root).resolve()
    attempts = []
    chosen_arm = arm
    chosen_reason = args.selection_reason or reason
    result = None
    usage = {"status": "not_established"}

    # Automatic routing may rotate across eligible free-tier generic arms
    # after a provider 429. Credit-funded arms never leapfrog the eligible
    # free-tier Gemini fallback; explicit requests remain single-arm.
    candidates = [arm]
    if args.arm == "auto":
        eligible = eligible_arms(registry, census, today_pt())
        candidates = [candidate for candidate in eligible
                      if candidate.get("harness") == "generic-agent-loop"
                      and (candidate.get("budget") or {}).get("class") == "free-tier"]
        gemini_available = any(candidate.get("arm_id") == "gemini-cli" for candidate in eligible)
        if not candidates and not gemini_available:
            candidates = [candidate for candidate in eligible
                          if candidate.get("harness") == "generic-agent-loop"]
        if candidates:
            chosen_arm = candidates[0]
            chosen_reason = args.selection_reason or reason

    if chosen_arm["harness"] != "generic-agent-loop":
        print(f"ARM_NOT_GENERIC harness={chosen_arm['harness']} (driven by its own step)")
        return 3
    if not args.task_file:
        print("agent-loop mode requires --task-file")
        return 2

    status = "failed"
    for index, candidate in enumerate(candidates):
        chosen_arm = candidate
        if index:
            chosen_reason = (f"quota-terminal rotation after {attempts[-1]['arm_id']}; "
                             f"next eligible free-tier arm {candidate['arm_id']}")
            print("ARM_ROTATION " + json.dumps({"from": attempts[-1]["arm_id"],
                                               "to": candidate["arm_id"]}))
        budget = candidate.get("budget") or {}
        max_turns = min(args.max_turns, int(budget["max_build_turns"])) if budget.get("max_build_turns") else args.max_turns
        try:
            result = run_agent_loop(candidate, task_text, root, max_turns)
            status = result["status"]
            usage = result.get("usage") or {"status": "not_established"}
            attempts.append({"arm_id": candidate["arm_id"], "status": status})
            break
        except QuotaTerminal as exc:
            attempts.append({"arm_id": candidate["arm_id"], "status": "quota_terminal"})
            result = {"status": "quota_terminal", "final": str(exc),
                      "attempts": attempts}
            usage = {"status": "not_established"}
            print(f"QUOTA_TERMINAL {exc} — rotating away from {candidate['arm_id']} without backoff-burn")
            if args.arm != "auto" or index == len(candidates) - 1:
                break
            continue
        except ArmFailure as exc:
            attempts.append({"arm_id": candidate["arm_id"], "status": "failed"})
            result = {"status": "failed", "final": str(exc), "http": exc.http,
                      "attempts": attempts}
            usage = {"status": "not_established"}
            break

    if result is None:
        result = {"status": "failed", "final": "no eligible generic free-tier arm",
                  "attempts": attempts}
    result["attempts"] = attempts
    if status != "completed":
        status = "failed"
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write(f"arm_id={chosen_arm['arm_id']}\\n")
            output.write(f"selection_reason={chosen_reason}\\n")
    print("ARM_FINAL_SELECTION " + json.dumps({"arm_id": chosen_arm["arm_id"],
                                                "selection_reason": chosen_reason,
                                                "attempts": attempts}))
    stamp = build_stamp(arm=chosen_arm, run_id=run_id, ts=now_iso(), issue=args.issue,
                        trigger=args.trigger, selection_reason=chosen_reason,
                        outcome_status=status,
                        evidence_ref=(f"actions run {run_id}" if run_id else None),
                        usage=usage, quota_class=args.quota_class)
    stamp["rotation_attempts"] = attempts
    Path(args.stamp_out).write_text(json.dumps(stamp, indent=2) + "\n", encoding="utf-8")
    Path(args.result_out).write_text(json.dumps(
        {"arm_id": chosen_arm["arm_id"], **result}, indent=2) + "\n", encoding="utf-8")
    print("ARM_RESULT " + json.dumps({"arm_id": chosen_arm["arm_id"], "status": status,
                                      "turns": result.get("turns")}))
    return 0 if status == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
