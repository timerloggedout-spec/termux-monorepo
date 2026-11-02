
## Tool acquisition routes (owner, 2026-11-01)

Full text: `docs/ops/TOOL-ACQUISITION-ROUTES.md`. Summary for every install/download task:
① Exec network calls ride an approval system — "Site always allowed" is decided per host by card (precedents: api.github.com, api.mistral.ai, mcp.deepwiki.com). ② Silent failure mode: downloads from non-whitelisted hosts (storage.googleapis.com, googlechromelabs.github.io) die at write (curl rc23/EPERM, 0-byte) with ∅ card generated — never report "platform-impossible"; correct report = "host not whitelisted ∧ no card engaged; route via ③/④". ③ Browser-channel downloads persist (~/workspace/browser_downloads). ④ GitHub-artifact route via api.github.com (precedent dd04486c). ⑤ Precedent: go.tgz 66.9MB + Go tree landed 2026-10-27.
