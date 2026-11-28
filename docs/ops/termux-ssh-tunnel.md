# Direct CLI access to a Termux device over a self-healing Pinggy tunnel

How an off-device agent or collaborator gets a key-only SSH shell on a Termux phone that sits behind NAT, with no paid tunnel, no open router ports, and no device-side typing after the first run.

```
[agent / collaborator] --ssh (key + pinned host key)--> tcp://<random>.a.free.pinggy.link:<port>
                                                             |
                                    Pinggy reverse tunnel (-R0:127.0.0.1:8022)
                                                             |
                                            Termux sshd :8022 (publickey only)
         endpoint rotates  -->  device posts new tcp:// URL to a private ntfy topic  -->  agent polls topic
```

## Why this shape
- Free Pinggy TCP tunnels expire after about 60 minutes, and the URL changes on every connection. The keeper loop reconnects, and ntfy carries the current endpoint, so clients follow the rotations automatically.
- Security doesn't depend on hiding the endpoint. sshd accepts public keys only, and clients pin the device's host key fingerprint, so a leaked URL or topic name gives no access.

## Device side (one time, in Termux)
Prereqs: `pkg install openssh curl termux-api`, plus the Termux:API app for notifications and wake lock.

1. Make sshd key-only. In `$PREFIX/etc/ssh/sshd_config`, set `PasswordAuthentication no` and `KbdInteractiveAuthentication no`. Check with `sshd -T | grep -i passwordauth`.
2. Authorize each collaborator's public key by appending it once to `~/.ssh/authorized_keys` (chmod 600). Use one key per person or agent, with a comment naming them, so you can revoke one by deleting its line.
3. Pick a long random ntfy topic, for example `openssl rand -hex 16`. Share it only with the people you've authorized.
4. Install the keeper as `~/.hark-tunnel.sh`, then `chmod 700`:

```bash
#!/data/data/com.termux/files/usr/bin/bash
T=<your-private-ntfy-topic>
while true; do
  ssh -tt -p 443 -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes \
    -R0:127.0.0.1:8022 -L4300:127.0.0.1:4300 tcp@free.pinggy.io >/dev/null 2>&1 &
  P=$!; last=""
  while kill -0 $P 2>/dev/null; do
    u=$(curl -s -m 5 127.0.0.1:4300/urls | grep -o 'tcp://[^"]*' | head -1)   # Pinggy local API
    if [ -n "$u" ] && [ "$u" != "$last" ]; then
      curl -s -m 10 -d "$u" "https://ntfy.sh/$T" >/dev/null && last="$u"
      termux-notification --id hark-tunnel -t "Tunnel" -c "$u" >/dev/null 2>&1
    fi
    sleep 20
  done
  sleep 10   # tunnel dropped or expired: reconnect
done
```

5. Start it: `pgrep -x sshd || sshd; termux-wake-lock; nohup ~/.hark-tunnel.sh >/dev/null 2>&1 &`. Add the same line to `~/.termux/boot/` (Termux:Boot) so it survives reboots.
6. Record the host key fingerprint once and send it to collaborators out of band: `ssh-keygen -lf $PREFIX/etc/ssh/ssh_host_ed25519_key.pub`.

## Client side (each collaborator)
```bash
# latest endpoint from the last 72h of the topic
U=$(curl -s "https://ntfy.sh/$TOPIC/json?poll=1&since=72h" | jq -r .message | grep tcp:// | tail -1)
H=${U#tcp://}; P=${H##*:}; H=${H%:*}
ssh -i ~/.ssh/termux_ed25519 -p "$P" -o StrictHostKeyChecking=yes termux@"$H" 'uname -a'
```
Pin the host key: put `[$H]:$P ssh-ed25519 <device host key>` in `known_hosts`, or compare the fingerprint in code, as the reference Python client below does. Because the host:port rotates, pinning by key fingerprint is simpler than pinning by `known_hosts` entry.

Reference Python client (paramiko), the one Hark uses:
```python
c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(H, P, username="termux", key_filename=KEY, allow_agent=False, look_for_keys=False, timeout=20)
k = c.get_transport().get_remote_server_key()
fp = "SHA256:" + base64.b64encode(hashlib.sha256(k.asbytes()).digest()).decode().rstrip("=")
assert fp == PINNED_FP, "HOSTKEY MISMATCH"   # refuse before running anything
```

## Operating rules
- Read-only recon (ls, cat, grep, git log, pgrep, df) is safe to run unattended. Restarts, edits, deletes, and anything that uses credentials need the device owner's OK.
- Never print or copy secrets from `~/.deepcli/` or other credential stores over the lane.
- To revoke someone, delete their key line from `authorized_keys`. Rotate the ntfy topic if it leaks; that's a nuisance, not a breach.
- Troubleshooting: no new ntfy message means the keeper isn't running (`pgrep -af hark-tunnel`) or the phone killed Termux (check wake lock and battery optimization). `Connection refused` means sshd is down (`sshd`). `HOSTKEY MISMATCH` means stop and investigate; don't override it.

## Limits
- Free Pinggy allows one tunnel at a time, with about 60 minutes per connection. Expect brief gaps during reconnects. The topic history keeps the latest endpoint.
- ntfy.sh topics are public by name. Use a long random topic, or self-host ntfy with access control.
