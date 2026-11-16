# Device identity (opaque IDs, sealed fingerprints)

Every Termux node has two separate things:

| | Public **device_id** | Private **fingerprint map** |
|---|---|---|
| Example | `tmx-node-55619bd5` | make, model, `ro.build.fingerprint`, serial, Android/SDK, patch level |
| Source | 4 random bytes from `/dev/urandom` | `getprop` on the device |
| Where it lives | `~/.config/tmx-device/identity.env` (0600), `ops/devices/registry.json`, heartbeats, `ops/termux-bridge/current.json` | age-encrypted only: GitHub secret `TMX_FPMAP_<SUFFIX>`, local `~/.config/tmx-device/sealed/<id>.fpmap.age`, optionally `ops/devices/sealed/<id>.fpmap.age` |
| Linkable to hardware? | No. Never derived from, hashed from, or salted with any hardware/build value | Yes, by design, only for holders of the age identity |

Both B160V phones share one Google account (`<operator Google account>`); the Google account is **not** a device identity and is never used as one.

## Rules

1. IDs match `^tmx-node-[a-z0-9][a-z0-9-]{3,31}$`. The origin keeps its existing id `tmx-node-primary` (PR #1245). New units get a random id.
2. A hash of a serial/IMEI is still a fingerprint. Do not derive IDs from hardware.
3. Plaintext fingerprints never touch disk or git: `getprop -> python -> age -a` in one pipe.
4. Anything committed is ciphertext (age; sops-compatible since sops supports age recipients).
5. `device-identity.sh init` refuses to overwrite an existing identity. Re-identifying a unit is a deliberate manual act.
6. Additive-only repo rule applies: sealed files are added, never replaced or deleted.

## Key setup (once)

On one trusted unit (or a workstation with `age`):

```bash
bash scripts/termux/devices/device-identity.sh keygen
# prints age1... public recipient
```

* Add the public `age1...` line to `ops/devices/age-recipients.txt` (new file, via PR).
* Keep the private key off-device (password manager). Optionally also:
  `gh secret set TMX_DEVICE_AGE_IDENTITY --repo timerloggedout-spec/termux-monorepo < ~/.config/tmx-device/operator-age.key`
* Then remove the private key from the phone if it was generated there.

## Per device

```bash
bash scripts/termux/devices/device-identity.sh init --id tmx-node-55619bd5 --role observer   # secondary
bash scripts/termux/devices/device-identity.sh init --id tmx-node-primary  --role bridge     # origin
bash scripts/termux/devices/device-identity.sh seal --secret            # -> GitHub secret TMX_FPMAP_<SUFFIX>
bash scripts/termux/devices/device-identity.sh seal --recipient age1... # if age-recipients.txt not merged yet
bash scripts/termux/devices/device-identity.sh verify                   # id/heartbeat leak check
```

GitHub secrets are write-only from the API. To read a map back, decrypt the local or committed `.age` file with the private key:

```bash
age -d -i operator-age.key ops/devices/sealed/tmx-node-55619bd5.fpmap.age
```

## Registry

`ops/devices/registry.json` lists ids, roles, job ids and the secret name for each node. It must never contain fingerprint values; `verify` checks this on-device.

## Related

* `scripts/termux/devices/` — provisioning, heartbeat, status notification, git guard
* `docs/ops/SECONDARY-NODE-PROVISIONING.md` — runbook
* `docs/ops/BRIDGE-REDUNDANCY.md` — execution hierarchy, opaque ID origin
