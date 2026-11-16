# AWS Emulator integration contract

This directory is a policy/metadata boundary, not an enabled runtime integration.

- `contract.json` is the machine-readable source for the initial local-only posture.
- `runtime_enabled` is false; no runner should start an emulator based on this record.
- `cloud_fallback` is deny; unsupported emulator behavior must remain visible.
- Credentials are synthetic only. Do not pass ambient AWS credentials or production data to emulator tests.
- Security testing is prohibited because the emulator is a development/test tool, not a security boundary.
- The default endpoint is loopback HTTPS only.

Validate the contract offline:

```sh
python3 scripts/ci/verify_aws_emulator_contract.py
python3 -m unittest discover -s tests -p 'test_aws_emulator_contract.py' -v
```

The validator does not install, start, or contact AWS Emulator. A supported-host pilot requires a separately reviewed pinned release and evaluation-suite revision, an isolated disposable environment, and exact-SHA evidence.
