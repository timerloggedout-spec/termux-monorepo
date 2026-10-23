"""No phones, network connections, process signals, or model requests in these tests."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'scripts/antigravity/secondary-recovery'
TERMUX_PREFIX = '/data/data/com.termux/files/usr'


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir='/dev/shm')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / 'home'
        self.prefix = self.root / 'prefix'
        self.bin = self.prefix / 'bin'
        self.bin.mkdir(parents=True)
        self.marker = self.home / '.local/share/agy-1497-secondary/worktree/.agy-secondary-id'
        self.marker.parent.mkdir(parents=True)
        self.marker.write_text('tmx-node-55619bd5\n')
        self.trace = self.root / 'trace'
        self.env = dict(os.environ, HOME=str(self.home), PREFIX=str(self.prefix),
                        PATH=f'{self.bin}:' + os.environ['PATH'], TRACE=str(self.trace))
        self.mock('whoami', 'echo "${TEST_USER:-u0_a243}"')
        self.mock('getprop', 'echo "${TEST_MODEL:-B160V}"')
        self.mock('termux-wake-lock', 'echo wake >> "$TRACE"')
        self.mock('sshd', 'echo "sshd $*" >> "$TRACE"')
        self.mock('sv-enable', 'echo "enable $*" >> "$TRACE"')
        self.mock('sv', 'echo "sv $*" >> "$TRACE"')
        self.mock('pgrep', 'exit 1')
        self.mock('sleep', 'echo sleep >> "$TRACE"')
        profile = self.prefix / 'etc/profile.d/start-services.sh'
        profile.parent.mkdir(parents=True)
        profile.write_text('export SVDIR="$PREFIX/var/service"\necho source >> "$TRACE"\n')
        self.service = self.prefix / 'var/service/tmx-secondary-sshd'
        self.service.mkdir(parents=True)
        run = self.service / 'run'
        run.write_text('#!/bin/sh\nexit 0\n')
        run.chmod(0o700)
        (self.service / 'supervise').mkdir()
        os.mkfifo(self.service / 'supervise/ok')
        self.src = self.root / 'source'
        self.src.mkdir()
        for p in SOURCE.iterdir():
            if p.is_file():
                # Only relocate the fixed Android prefix in isolated Linux fixtures.
                data = p.read_text().replace(TERMUX_PREFIX, str(self.prefix))
                data = data.replace(f'#!{self.prefix}/bin/bash', '#!/bin/bash')
                (self.src / p.name).write_text(data)
                (self.src / p.name).chmod(0o700)
        self.mock('zsh', 'exit 0')

    def mock(self, name, body):
        p = self.bin / name
        p.write_text('#!/bin/sh\n' + body + '\n')
        p.chmod(0o700)

    def run_script(self, name, **env):
        return subprocess.run(['bash', str(self.src / name)], env=dict(self.env, **env),
                              text=True, capture_output=True, timeout=5)

    def trace_lines(self):
        return self.trace.read_text().splitlines() if self.trace.exists() else []

    def test_wrong_node_rejected_before_reconnect_effects(self):
        self.marker.write_text('tmx-node-primary\n')
        self.assertEqual(self.run_script('tmx-reconnect').returncode, 21)
        self.assertEqual(self.trace_lines(), [])

    def test_symlink_marker_rejected(self):
        actual = self.marker.with_name('actual')
        self.marker.rename(actual)
        self.marker.symlink_to(actual)
        self.assertEqual(self.run_script('tmx-reconnect').returncode, 21)

    def test_wrong_user_rejected(self):
        self.assertEqual(self.run_script('tmx-reconnect', TEST_USER='other').returncode, 23)
        self.assertEqual(self.trace_lines(), [])

    def test_wrong_model_rejected(self):
        self.assertEqual(self.run_script('tmx-reconnect', TEST_MODEL='other').returncode, 23)

    def test_wrong_prefix_rejected(self):
        self.assertEqual(self.run_script('tmx-reconnect', PREFIX='/wrong').returncode, 24)

    def test_reconnect_is_non_killing_and_repeatable(self):
        for _ in range(2):
            result = self.run_script('tmx-reconnect')
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.trace_lines().count('wake'), 2)
        self.assertEqual(self.trace_lines().count('enable tmx-secondary-sshd'), 2)
        for line in self.trace_lines():
            self.assertNotIn('restart', line)
            self.assertNotIn('kill', line)
        self.assertNotIn('ssh-keygen', (self.src / 'tmx-reconnect').read_text())

    def test_missing_service_rejected(self):
        (self.service / 'run').unlink()
        self.assertEqual(self.run_script('tmx-reconnect').returncode, 25)

    def test_foreground_service_execs_sshd(self):
        result = self.run_script('sshd-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.trace_lines(), ['sshd -t', 'sshd -D -e'])

    def test_manual_daemon_waited_for_without_signal(self):
        self.mock('pgrep', 'nfile="$HOME/count"; n=0; [ ! -f "$nfile" ] || n=$(cat "$nfile"); n=$((n+1)); echo "$n" > "$nfile"; [ "$n" -lt 3 ]')
        result = self.run_script('sshd-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('not yet a supervised listener', result.stdout)
        self.assertEqual(self.trace_lines(), ['sleep', 'sshd -t', 'sshd -D -e'])

    def test_boot_requests_wake_before_profile_and_reconnect(self):
        localbin = self.home / '.local/bin'
        localbin.mkdir(parents=True)
        reconnect = localbin / 'tmx-reconnect'
        reconnect.write_text('#!/bin/sh\necho reconnect >> "$TRACE"\n')
        reconnect.chmod(0o700)
        result = self.run_script('10-tmx-secondary-services')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.trace_lines(), ['wake', 'source', 'reconnect'])

    def test_installer_preserves_unrelated_zshrc_and_is_idempotent(self):
        zshrc = self.home / '.zshrc'
        zshrc.write_text('export UNRELATED=keep\n')
        for _ in range(2):
            result = self.run_script('install.sh')
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(zshrc.read_text().startswith('export UNRELATED=keep\n'))
        self.assertEqual(zshrc.read_text().count('# BEGIN tmx-secondary-reconnect'), 1)
        self.assertEqual((self.prefix / 'var/log/sv/tmx-secondary-sshd/config').read_text(), 's65536\nn2\n')

    def test_new_zshrc_is_recorded_for_rollback(self):
        result = self.run_script('install.sh')
        self.assertEqual(result.returncode, 0, result.stderr)
        backups = list((self.home / '.local/state/tmx-secondary-recovery').glob('install-before.*'))
        self.assertEqual(len(backups), 1)
        self.assertIn(str(self.home / '.zshrc'), (backups[0] / 'created-paths').read_text())

    def test_missing_zsh_rejected_before_mutation(self):
        zsh = self.bin / 'zsh'
        zsh.unlink()
        result = self.run_script('install.sh')
        self.assertEqual(result.returncode, 30)
        self.assertIn('zsh', result.stderr)
        self.assertFalse((self.home / '.zshrc').exists())
        self.assertFalse((self.service / 'down').exists())

    def test_installer_refuses_enabled_stock_sshd(self):
        (self.prefix / 'var/service/sshd').mkdir()
        result = self.run_script('install.sh')
        self.assertEqual(result.returncode, 28)
        self.assertNotIn('rollback snapshot', result.stderr)

    def test_installer_refuses_symlink_target(self):
        (self.service / 'run').unlink()
        (self.service / 'run').symlink_to(self.root / 'victim')
        self.assertEqual(self.run_script('install.sh').returncode, 29)
        self.assertFalse((self.root / 'victim').exists())


if __name__ == '__main__':
    unittest.main()
