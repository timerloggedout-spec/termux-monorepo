#!/usr/bin/env python3
"""DO append one JSON line to a file in a GitHub repo via the contents API (fast-forward commit, ¬ force).

Usage: append_jsonl.py OWNER/REPO PATH COMMIT_MSG < line.json
Auth: `gh api` with GH_TOKEN. Retries on 409/422 sha races. Prints the new commit sha.
"""
import base64, json, subprocess, sys, time

def gh(*args, data=None):
    p = subprocess.run(["gh", "api", *args], input=data, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

def main():
    repo, path, msg = sys.argv[1:4]
    line = json.dumps(json.loads(sys.stdin.read()), ensure_ascii=False, separators=(",", ":"))
    for attempt in range(5):
        rc, out, err = gh(f"repos/{repo}/contents/{path}")
        sha, body = None, ""
        if rc == 0:
            meta = json.loads(out)
            sha, body = meta["sha"], base64.b64decode(meta["content"]).decode()
        elif "Not Found" not in out + err:
            sys.exit(f"::error title=append::read {path} rc={rc}")
        if body and not body.endswith("\n"):
            body += "\n"
        payload = {"message": msg, "content": base64.b64encode((body + line + "\n").encode()).decode()}
        if sha:
            payload["sha"] = sha
        rc, out, err = gh("-X", "PUT", f"repos/{repo}/contents/{path}", "--input", "-", data=json.dumps(payload))
        if rc == 0:
            print(json.loads(out)["commit"]["sha"])
            return
        if "409" in err or "422" in err or "does not match" in out:
            time.sleep(2 + attempt * 3)
            continue
        sys.exit(f"::error title=append::write {path} rc={rc} {err.strip()[:200]}")
    sys.exit("::error title=append::sha race persisted after 5 attempts")

if __name__ == "__main__":
    main()
