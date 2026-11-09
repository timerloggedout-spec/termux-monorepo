## Summary

The public-SSH HOLD gate currently accepts generic `auth` and `password_auth` flags as sufficient protection. That allows a request exposing sshd to the public internet with password authentication only to pass the safety gate.

## Change

Require an explicit key-authentication signal (`key_auth`, `use_key`, or `public_key_auth`) whenever public SSH exposure is requested. Generic `auth` and password flags no longer clear the gate. The existing `sshd_public_no_auth` trigger is retained for compatibility.

## Regression coverage

Adds parameterized tests for:
- no authentication;
- generic `auth=True`;
- password-only authentication;
- password-authentication aliases;
- all supported explicit key-authentication aliases.

## Acceptance criteria

- [ ] Public SSH without explicit key auth is held.
- [ ] Password-only public SSH remains held even if generic `auth=True`.
- [ ] Explicit key-auth flags clear this specific gate.
- [ ] Existing HOLD trigger name remains unchanged.
- [ ] Full CI passes: `python -m pytest tests/ -q` and `python main.py`.

This is a narrow safety correction. Key authentication does not replace firewalling, network segmentation, or other SSH hardening.
