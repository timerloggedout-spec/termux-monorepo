"""Offline fixtures only: no device, network, AGY, or credentials."""
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PATH = Path(__file__).resolve().parents[1] / "scripts/antigravity/access_preflight.py"
SPEC = importlib.util.spec_from_file_location("agy_access_preflight", PATH)
access = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = access
SPEC.loader.exec_module(access)
R = access.Result


class AccessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pin = Path(self.tmp.name) / "known_hosts.device2"
        self.pin.write_text("fixture pin, not a key\n")
        self.config = ("hostname 100.64.0.2\nuser u0_a243\nport 8022\n"
                       "hostkeyalias b160v-1\nstricthostkeychecking true\n"
                       f"userknownhostsfile {self.pin}\nproxycommand fixture-proxy %h %p\n")
        self.ts = R(0, json.dumps({"BackendState": "Running", "Peer": {
            "fixture-key": {"ID": "fixture-id", "Online": True, "TailscaleIPs": ["100.64.0.2"]}}}))
        self.identity = R(0, "ACCESS_IDENTITY_OK\n")
        self.checks = R(0, "ACCESS_IDENTITY_OK\nGH_AUTH_OK\nGH_API_OK\nGIT_REMOTE_OK\nACCESS_CHECKS_DONE\n")

    def invoke(self, results=None, config=None, ts=None, attempts=3):
        queued = [R(0, self.config if config is None else config), self.ts if ts is None else ts,
                  *(results if results is not None else [self.identity, self.checks])]
        calls, sleeps = [], []

        def runner(command, timeout):
            calls.append((command, timeout))
            return queued.pop(0)

        report, code = access.preflight(attempts, runner=runner, sleep=sleeps.append)
        return report, code, calls, sleeps

    def test_success_has_three_separate_proofs(self):
        report, code, calls, sleeps = self.invoke()
        self.assertEqual(code, 0)
        self.assertTrue(report["ready"])
        self.assertEqual(report["tailscale"]["peer"], "online")
        self.assertFalse(report["tailscale"]["ssh_ready"])
        self.assertEqual(report["ssh"]["authentication"], "verified")
        self.assertEqual(report["git_remote"], "verified")
        self.assertEqual(len(calls), 4)
        self.assertEqual(sleeps, [])
        self.assertEqual(report["tasks_launched"], 0)
        self.assertFalse(report["replay_permitted"])

    def test_online_tailnet_is_not_ssh_readiness(self):
        report, code, calls, _ = self.invoke([R(255, stderr="Permission denied (publickey).")])
        self.assertEqual(code, 20)
        self.assertFalse(report["ready"])
        self.assertEqual(report["tailscale"]["peer"], "online")
        self.assertEqual(report["ssh"]["listener"], "reachable")
        self.assertEqual(report["ssh"]["authentication"], "rejected")
        self.assertEqual(report["git_remote"], "not_checked")
        self.assertEqual(len(calls), 3)

    def test_transient_establishment_recovers_with_bounded_backoff(self):
        report, code, calls, sleeps = self.invoke([
            R(255, stderr="connect to host fixture port 8022: Connection refused"),
            R(255, stderr="kex_exchange_identification: Connection closed by remote host"),
            self.identity, self.checks])
        self.assertEqual(code, 0)
        self.assertEqual(report["ssh"]["attempts"], 3)
        self.assertEqual(report["ssh"]["listener"], "reachable")
        self.assertEqual(sleeps, [1, 2])
        self.assertEqual(sum(c[-1] == access.GITHUB_GIT for c, _ in calls), 1)

    def test_retries_exhaust_only_establishment(self):
        report, code, calls, sleeps = self.invoke([R(255, stderr="Connection refused")] * 3)
        self.assertEqual(code, 20)
        self.assertEqual(report["ssh"]["attempts"], 3)
        self.assertEqual(report["ssh"]["listener"], "refused")
        self.assertEqual(sleeps, [1, 2])
        self.assertFalse(any(c[-1] == access.GITHUB_GIT for c, _ in calls))

    def test_single_attempt_option(self):
        report, code, calls, sleeps = self.invoke([R(255, stderr="Connection refused")], attempts=1)
        self.assertEqual(code, 20)
        self.assertEqual(report["ssh"]["attempts"], 1)
        self.assertEqual(sleeps, [])

    def test_terminal_errors_never_retry(self):
        for error in ("Host key verification failed.", "REMOTE HOST IDENTIFICATION HAS CHANGED!",
                      "No ED25519 host key is known", "Permission denied (publickey).",
                      "Too many authentication failures", "Bad configuration option", "arbitrary transport error"):
            with self.subTest(error=error):
                report, code, calls, sleeps = self.invoke([R(255, stderr=error)])
                self.assertEqual(code, 20)
                self.assertEqual(len(calls), 3)
                self.assertEqual(sleeps, [])

    def test_identity_rejection_never_runs_github_checks(self):
        report, code, calls, _ = self.invoke([R(21)])
        self.assertEqual(code, 20)
        self.assertEqual(report["reason"], "secondary_identity_rejected")
        self.assertEqual(report["ssh"]["authentication"], "identity_rejected")
        self.assertEqual(len(calls), 3)

    def test_missing_handshake_marker_is_unknown_not_success(self):
        report, code, calls, _ = self.invoke([R(0, "unexpected output\n")])
        self.assertEqual(code, 20)
        self.assertEqual(len(calls), 3)
        self.assertFalse(report["ready"])

    def test_whole_handshake_deadline_is_not_retried(self):
        report, code, calls, sleeps = self.invoke([R(124, timed_out=True)])
        self.assertEqual(code, 20)
        self.assertEqual(report["reason"], "deadline_unknown")
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleeps, [])

    def test_github_disconnect_never_reconnects_or_replays(self):
        report, code, calls, sleeps = self.invoke([
            self.identity, R(255, "ACCESS_IDENTITY_OK\nGH_AUTH_OK\n", "Connection reset by peer")])
        self.assertEqual(code, 30)
        self.assertEqual(report["ssh"]["authentication"], "verified")
        self.assertEqual(report["github_cli_auth"], "unknown")
        self.assertEqual(report["git_remote"], "unknown")
        self.assertEqual(report["reason"], "github_git_outcome_unknown_no_replay")
        self.assertEqual(len(calls), 4)
        self.assertEqual(sleeps, [])

    def test_github_deadline_is_unknown_and_not_retried(self):
        report, code, calls, _ = self.invoke([self.identity, R(124, timed_out=True)])
        self.assertEqual(code, 30)
        self.assertEqual(report["github_api"], "unknown")
        self.assertEqual(len(calls), 4)

    def test_read_only_checks_fail_independently(self):
        for field, token in (("github_cli_auth", "GH_AUTH"), ("github_api", "GH_API"),
                             ("git_remote", "GIT_REMOTE")):
            with self.subTest(field=field):
                result = R(0, self.checks.stdout.replace(token + "_OK", token + "_UNVERIFIED"))
                report, code, calls, _ = self.invoke([self.identity, result])
                self.assertEqual(code, 31)
                self.assertEqual(report[field], "not_verified")
                self.assertEqual(len(calls), 4)

    def test_missing_remote_timeout_does_not_launch_network_checks(self):
        report, code, calls, _ = self.invoke([self.identity, R(22, "ACCESS_IDENTITY_OK\nDEADLINE_UNAVAILABLE\n")])
        self.assertEqual(code, 30)
        self.assertEqual(len(calls), 4)

    def test_per_command_deadline_and_unavailable_are_not_auth_rejections(self):
        for token, status in (("DEADLINE", "deadline_unknown"), ("UNAVAILABLE", "unavailable")):
            result = R(0, self.checks.stdout.replace("GH_AUTH_OK", "GH_AUTH_" + token))
            report, code, calls, _ = self.invoke([self.identity, result])
            self.assertEqual(code, 31)
            self.assertEqual(report["github_cli_auth"], status)
            self.assertEqual(len(calls), 4)

    def test_handshake_output_or_post_auth_close_never_retries(self):
        for result in (R(255, "ACCESS_IDENTITY_OK\n", "Connection refused"),
                       R(255, stderr="Connection reset by peer")):
            report, code, calls, sleeps = self.invoke([result])
            self.assertEqual(code, 20)
            self.assertEqual(len(calls), 3)
            self.assertEqual(sleeps, [])

    def test_remote_result_protocol_is_exact_not_forgiving(self):
        for output in (self.checks.stdout + "extra\n",
                       self.checks.stdout.replace("GH_AUTH_OK", "GH_AUTH_OK\nGH_AUTH_UNVERIFIED")):
            report, code, _, _ = self.invoke([self.identity, R(0, output)])
            self.assertEqual(code, 30)
            self.assertEqual(report["github_cli_auth"], "unknown")

    def test_remote_shell_deadlines_and_git_configuration_isolation(self):
        root = Path(self.tmp.name)
        home, binaries = root / "home", root / "bin"
        home.mkdir()
        binaries.mkdir()
        marker = home / ".local/share/agy-1497-secondary/worktree/.agy-secondary-id"
        marker.parent.mkdir(parents=True)
        marker.write_text("tmx-node-55619bd5\n")
        # A hostile config must not supply a helper or rewrite the fixed URL.
        (home / ".gitconfig").write_text(
            '[credential]\n helper = !touch NEVER_EXECUTE_HELPER\n'
            '[url "https://untrusted.invalid/"]\n insteadOf = https://github.com/\n')

        def script(name, text):
            target = binaries / name
            target.write_text("#!/bin/sh\n" + text + "\n")
            target.chmod(0o700)

        script("whoami", "echo u0_a243")
        script("getprop", "echo B160V")
        script("gh", 'exit "${FIXTURE_GH_CODE:-0}"')
        script("timeout", 'test "$1 $2" = "-k 2" || exit 99\nshift 3\n'
               '[ "${FIXTURE_TIMEOUT_CODE:-0}" = 0 ] || exit "$FIXTURE_TIMEOUT_CODE"\nexec "$@"')
        real_git = shutil.which("git")
        self.assertIsNotNone(real_git)
        # Exercise actual Git config resolution with the exact probe arguments,
        # replacing only the final network operation with config inspection.
        script("git", f'exec "{sys.executable}" "{root / "git_check.py"}" "$@"')
        (root / "git_check.py").write_text(
            "import subprocess,sys\n"
            "args=sys.argv[1:]\n"
            "assert args[-4:]==['ls-remote','--exit-code'," + repr(access.REPOSITORY) + ",'HEAD']\n"
            "base=[" + repr(real_git) + "]+args[:-4]\n"
            "helper=subprocess.run(base+['config','--get','credential.helper'],capture_output=True,text=True)\n"
            "assert helper.returncode==0 and helper.stdout=='\\n',helper\n"
            "rewrite=subprocess.run(base+['config','--get-regexp','^url\\\\.'],capture_output=True)\n"
            "assert rewrite.returncode==1 and not rewrite.stdout,rewrite\n")
        env = dict(os.environ, HOME=str(home), PATH=str(binaries) + os.pathsep + os.environ["PATH"],
                   GIT_CONFIG_GLOBAL=str(home / ".gitconfig"),
                   GIT_CONFIG_PARAMETERS="'credential.helper'='!never-run'")
        for extra, expected in (({}, "GH_AUTH_OK\nGH_API_OK\nGIT_REMOTE_OK"),
                                ({"FIXTURE_TIMEOUT_CODE": "124"}, "GH_AUTH_DEADLINE\nGH_API_DEADLINE\nGIT_REMOTE_DEADLINE"),
                                ({"FIXTURE_GH_CODE": "1"}, "GH_AUTH_UNVERIFIED\nGH_API_UNVERIFIED\nGIT_REMOTE_OK")):
            result = subprocess.run(["bash", "-c", access.GITHUB_GIT], env=dict(env, **extra),
                                    capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(expected, result.stdout)
            self.assertTrue(result.stdout.endswith("ACCESS_CHECKS_DONE\n"))
        self.assertFalse((root / "NEVER_EXECUTE_HELPER").exists())

    def test_offline_peer_still_gets_fresh_ssh_diagnosis(self):
        ts = R(0, self.ts.stdout.replace('"Online": true', '"Online": false'))
        report, code, _, _ = self.invoke(ts=ts)
        self.assertEqual(code, 0)
        self.assertEqual(report["tailscale"]["peer"], "offline")
        self.assertEqual(report["ssh"]["authentication"], "verified")

    def test_tailnet_unknown_cases_do_not_claim_ssh(self):
        for ts in (R(127), R(124, timed_out=True), R(0, "not json"), R(0, "[]"),
                   R(0, '{"Peer": []}'), R(0, '{"BackendState":"Stopped","Peer":{}}')):
            with self.subTest(ts=ts):
                report, code, _, _ = self.invoke(ts=ts)
                self.assertEqual(code, 0)
                self.assertEqual(report["tailscale"]["peer"], "unknown")
                self.assertFalse(report["tailscale"]["ssh_ready"])

    def test_peer_address_match_not_fuzzy_name(self):
        ts = R(0, '{"BackendState":"Running","Peer":{"termux-device2":{"Online":true,"TailscaleIPs":["100.64.0.3"]}}}')
        report, _, _, _ = self.invoke(ts=ts)
        self.assertEqual(report["tailscale"]["peer"], "unknown")

    def test_unpinned_or_wrong_secondary_config_stops_before_network(self):
        for old, new in (("b160v-1", "origin"), ("u0_a243", "other"), ("8022", "22"),
                         ("100.64.0.2", "192.168.1.1"), ("100.64.0.2", "example.com"),
                         ("true", "false"), (str(self.pin), "/dev/null"),
                         ("fixture-proxy %h %p", "none")):
            with self.subTest(old=old):
                report, code, calls, _ = self.invoke(config=self.config.replace(old, new))
                self.assertEqual(code, 10)
                self.assertEqual(len(calls), 1)
                self.assertEqual(report["reason"], "pinned_secondary_config_required")

    def test_missing_existing_pin_file_stops(self):
        self.pin.unlink()
        report, code, calls, _ = self.invoke()
        self.assertEqual(code, 10)
        self.assertEqual(len(calls), 1)

    def test_ssh_policy_preserves_pinning_and_disables_side_effects(self):
        _, _, calls, _ = self.invoke()
        for command, deadline in (calls[0], calls[2], calls[3]):
            for value in ("StrictHostKeyChecking=yes", "UpdateHostKeys=no", "BatchMode=yes",
                          "ConnectionAttempts=1", "ControlPath=none", "AddKeysToAgent=no",
                          "ClearAllForwardings=yes", "PermitLocalCommand=no", "ForwardAgent=no"):
                self.assertIn(value, command)
            self.assertLessEqual(deadline, 45)
        self.assertEqual(calls[2][0][-2], "termux-device2")
        self.assertEqual(calls[3][0][-1], access.GITHUB_GIT)

    def test_no_raw_diagnostics_or_credentials_in_report(self):
        private = "PRIVATE_URL_TOKEN_PATH_username"
        report, _, _, _ = self.invoke([R(255, private, private)])
        self.assertNotIn(private, json.dumps(report))
        self.assertNotIn(str(self.pin), json.dumps(report))
        self.assertNotIn("100.64.0.2", json.dumps(report))

    def test_no_arbitrary_task_or_host_cli_arguments(self):
        for args in (["--command", "agy"], ["--host", "origin"], ["--attempts", "0"], ["--attempts", "4"]):
            with self.subTest(args=args), patch("sys.stderr", new=io.StringIO()):
                with self.assertRaises(SystemExit) as exit:
                    access.main(args)
                self.assertEqual(exit.exception.code, 2)

    def test_retry_argument_checked_for_direct_callers(self):
        for attempts in (0, 4, 100):
            with self.assertRaises(ValueError):
                access.preflight(attempts, runner=lambda *_: self.fail("must not run"))

    def test_existing_local_socket_is_passed_only_to_status(self):
        calls = []
        def runner(command, timeout):
            calls.append(command)
            return self.ts
        access.tailnet_status("100.64.0.2", "/fixture/tailscaled.sock", runner)
        self.assertEqual(calls, [["tailscale", "--socket=/fixture/tailscaled.sock", "status", "--json"]])

    def test_fixed_remote_checks_do_not_mutate_or_run_agy(self):
        self.assertIn("probe GH_AUTH 10 gh auth status", access.GITHUB_GIT)
        self.assertIn("probe GH_API 10 gh api", access.GITHUB_GIT)
        self.assertIn("probe GIT_REMOTE 15 git", access.GITHUB_GIT)
        self.assertIn("GIT_TERMINAL_PROMPT=0", access.GITHUB_GIT)
        self.assertIn("GIT_OPTIONAL_LOCKS=0", access.GITHUB_GIT)
        self.assertIn(access.REPOSITORY, access.GITHUB_GIT)
        for forbidden in ("agy --", "gh auth login", "gh auth setup-git", "git fetch", "git pull",
                          "sv-enable", "termux-wake-lock", "tailscale up"):
            self.assertNotIn(forbidden, access.GITHUB_GIT)

    def test_process_runner_bounds_and_kills_descendants(self):
        result = access.run([sys.executable, "-c", "import time; time.sleep(30)"], 1)
        self.assertEqual(result.code, 124)
        self.assertTrue(result.timed_out)

    def test_process_runner_missing_executable(self):
        self.assertEqual(access.run(["/not-an-executable-fixture"], 1).code, 127)

    def test_process_runner_success(self):
        result = access.run([sys.executable, "-c", "print('fixture')"], 2)
        self.assertEqual(result.code, 0)
        self.assertEqual(result.stdout, "fixture\n")


if __name__ == "__main__":
    unittest.main()
