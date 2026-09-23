# Termux Hub — Tailscale Connection & Collaborator Bootstrap

## Scope

This is the project-owned Android/Termux connection lane. It is intentionally independent of Desktop Commander.

The steady-state transport is:

```text
MCP client / operator
        |
        | authenticated SSH over private tailnet
        v
Tailscale / MagicDNS
        |
        v
termux-hub:8022
        |
        v
Termux MCP adapter
        |
        v
hub_mcp capability policy
        |
        +--> bounded shell / repository checks
        +--> Termux:API
        +--> optional Shizuku/rish
```

Tailscale supplies private network reachability; it does not itself provide a shell service. A service such as Termux OpenSSH must be listening on the destination. citeturn0search0turn0search3

## Canonical identity

Use the MagicDNS name as the stable connection identifier:

```text
termux-hub.tail4e1138.ts.net
```

The observed address `100.91.23.64` is useful for diagnostics, but must not be hard-coded into repository configuration. MagicDNS is designed to provide stable device names inside the tailnet. citeturn0search1

## Device bootstrap

Run on the Android Termux device:

```bash
pkg update
pkg install openssh git python termux-api
```

Create the SSH authorization directory:

```bash
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
touch "$HOME/.ssh/authorized_keys"
chmod 600 "$HOME/.ssh/authorized_keys"
```

Append the **collaborator's public key** to `authorized_keys`. Never copy a private key onto the device for this purpose.

Start the Termux SSH daemon:

```bash
sshd
```

Termux's OpenSSH package uses port `8022` by default; the upstream Termux package configuration explicitly patches the default port away from privileged port 22. citeturn1search0turn1search3

Verify locally:

```bash
printf 'user=%s\\n' "$(whoami)"
printf 'tailscale_host=termux-hub.tail4e1138.ts.net\\n'
tailscale ip -4
pgrep -a sshd || true
```

## Client profile

The collaborator's SSH client should use a key-only profile similar to:

```sshconfig
Host termux-hub
    HostName termux-hub.tail4e1138.ts.net
    Port 8022
    User <TERMUX_USER>
    IdentityFile ~/.ssh/<COLLABORATOR_KEY>
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

Then:

```bash
ssh termux-hub 'printf "connected\\n"; id; uname -a; printf "tailscale="; tailscale ip -4'
```

Tailscale documents both MagicDNS hostnames and Tailscale IPs as valid SSH destinations; access still depends on an SSH service being available on the destination. citeturn0search0turn0search1

## MCP launch contract

Do not expose an arbitrary shell string directly as the MCP policy surface.

The remote MCP client should launch the reviewed, pinned Termux MCP server through SSH, while the device-side server remains behind the project's `hub_mcp` capability policy.

Reference shape:

```json
{
  "mcpServers": {
    "termux-hub": {
      "command": "ssh",
      "args": [
        "-o", "BatchMode=yes",
        "-o", "IdentitiesOnly=yes",
        "-p", "8022",
        "termux-hub",
        "<PINNED_MCP_PYTHON>",
        "<PINNED_MCP_SERVER>"
      ]
    }
  }
}
```

Replace placeholders locally. Do not commit private keys, live host-specific paths, tunnel URLs, access tokens, or device exports.

## Shizuku boundary

Shizuku/rish is an **optional Android capability adapter**, not a prerequisite for shell connectivity.

Health should report these independently:

- `tailscale`: tailnet control/route state
- `ssh`: Termux OpenSSH listener
- `termux_mcp`: MCP server process/handshake
- `shizuku`: privileged Android bridge
- `hub_policy`: capability-policy readiness

A green SSH check must never be interpreted as proof that Shizuku is installed or authorized.

## Boot persistence

If Termux:Boot is installed and enabled, a small boot hook can start the SSH service after reboot. Keep it deterministic and avoid starting the MCP server blindly:

```bash
#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
pgrep -x sshd >/dev/null 2>&1 || sshd
```

The project should verify boot behavior on the target Android build rather than assuming Android will execute a boot hook reliably.

## Collaborator onboarding

1. Join the authorized tailnet.
2. Generate a local SSH key if one does not already exist.
3. Add only the public key to the device's `authorized_keys`.
4. Use the `termux-hub` SSH profile above.
5. Run the read-only health script:
   ```bash
   sh ./scripts/termux-hub/health.sh
   ```
6. Record the output as operational evidence, after removing host/user identifiers where they are not needed.
7. Only then enable the reviewed MCP client configuration.

No collaborator should receive the device's private SSH key, Tailscale auth key, MCP bearer token, OTP seed, password-store contents, or other long-lived secret.

## Fallback hierarchy

1. **Primary:** Tailscale + Termux OpenSSH on 8022.
2. **Secondary:** an authenticated private bridge/SSH route if a separate bridge host is available.
3. **Emergency:** existing reverse-SSH/Pinggy path, treated as ephemeral and never committed.
4. **Privileged Android:** Shizuku/rish adapter, independently health-checked.

The free Pinggy tunnel output observed during diagnostics expires and changes endpoints; it is therefore unsuitable as the canonical collaborator address.

## Evidence gate

Do not mark this lane "connected" merely because Tailscale shows green.

Minimum evidence:

```text
tailscale connected
+ sshd listening on 8022
+ key-only SSH round-trip succeeds
+ pinned MCP process starts
+ MCP initialize/health succeeds
+ hub_mcp policy remains enforced
```

The first successful command should be a harmless identity/readiness probe, not a mutation.

## Security invariants

- No public SSH exposure.
- No password-based collaborator onboarding.
- No arbitrary caller-supplied executable in the governed MCP contract.
- No TOTP seed or second-factor secret in MCP output or telemetry.
- No private keys in Git.
- No tunnel endpoints in tracked configuration.
- No Shizuku privilege escalation through an unreviewed adapter.
- Transport authentication and capability authorization remain separate gates.
