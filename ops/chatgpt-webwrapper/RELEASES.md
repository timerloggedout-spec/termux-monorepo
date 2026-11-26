# webWrapper Release Registry (comparative)

Owner mandate (firsthand, main chat, 2026-11-26 10:49 PT): "These ChatGPT DeepCLI etc webWrappers require their own release lanes & versions (comparative)."

Standing rules:
- Each webWrapper surface carries its OWN release lane with its OWN version lineage. A wrapper release bumps only its own lane's version.
- This table is the comparative cross-check surface across lanes — not one shared version stream.
- New wrappers enter as new lanes (new rows), never as versions of an existing lane.

| Wrapper | Lane | Version | Artifact | sha256 | Status | Date |
|---|---|---|---|---|---|---|
| ChatGPT webWrapper | `ops/chatgpt-webwrapper/termux/` | v1 (Selenium shape) | `termux-bundle.tar.gz` | NOT_ESTABLISHED in this registry | SUPERSEDED — doctor-failed on device (no chromedriver in Termux repos; Selenium port rejected) | 2026-11-26 |
| ChatGPT webWrapper | `ops/chatgpt-webwrapper/termux2/` | v2 (deepcli `core.py` shape + ADB import leg) | `termux2-bundle.tar.gz` (28,561 B) | `bf84f10cb1b9f0a37ad63e397f57a06d65583be252e48dc8d6fc6d2e7341be7d` | CURRENT | 2026-11-26 |
| DeepCLI | upstream reference (`deepcli/deepcli`) | NOT_ESTABLISHED from here | `core.py` (session-layer driver pattern) | — | REFERENCE — the shape v2 is built on; not a fleet release lane | 2026-11-26 |

Mandate stamps: QUE #5885 c.7200917411 · QUE #5920 c.7200918534.
