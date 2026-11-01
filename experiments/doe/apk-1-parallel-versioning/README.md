# apk-1-parallel-versioning

`[MUSEai]@{role:{apk-release}}` — DoE campaign: parallel versioning comparisons for the fleet `.APK` lane.

Owner order (2026-10-31): app builds go through **Termux MonoRepo dispatch methods** (provider dispatch routes of record), compared as a DoE. Design committed FIRST (`DESIGN.json`); builders ≠ evaluator; evaluator consumes committed evidence only.

| Arm | Version | Provider | Dispatch route |
|---|---|---|---|
| A | 0.2.1 | Jules | issue + `jules` label (`agent-jules-on-issues.yml`) |
| B | 0.2.2 | Gemini | issue + `@gemini-cli` invoke (`gemini-dispatch.yml`) |
| C | 0.2.3 | DeepSeek | `workflow_dispatch` (`deepseek-termux-agent.yml`, `task` input) |

Frozen spec (all arms): `apps/fleet-apk` — runtime version/SDK display in MainActivity, VERSION bump to arm version, CHANGELOG entry. Build proof per arm: `apk-release` dispatch at PR head ⇒ prerelease `apk-v<version>` with checksum-verified artifact. Selection/merges wait for the evaluator verdict (see DESIGN.json).
