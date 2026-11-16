# Tool acquisition routes — install/download rules for lanes

Owner codify order 2026-11-01 (learned the hard way, Devin-episode day). Applies to every lane task that installs or downloads a tool/binary/artifact from an agent VM. Also carried in root `CLAUDE.md` §Tool acquisition routes.

## Rules

1. **Exec network calls ride an approval system.** Calls from the VM to API hosts are gated by approval cards; a host becomes usable when the card decides "Site always allowed" for it. Precedents on record: `api.github.com` (artifact zip fetch+write APPROVED ∧ ran, 2026-11-01 13:24Z) · `api.mistral.ai` always-allowed · `mcp.deepwiki.com` always-allowed.
2. **Silent failure mode — never misreport it.** Binary/large downloads from non-whitelisted hosts (e.g. `storage.googleapis.com`, `googlechromelabs.github.io`) die at write time (curl rc23 / EPERM, 0-byte file) and **no approval card is generated**. This is NOT "platform-impossible". Correct report: "host not whitelisted ∧ no card engaged; route via ③/④".
3. **Browser-channel downloads persist.** Files fetched through the browser land in `~/workspace/browser_downloads` and survive; use the browser channel for browser-reachable downloads.
4. **GitHub-artifact route.** Fetch via `api.github.com` (whitelisted per ①) — e.g. Actions artifacts / release assets through the API instead of direct CDN hosts (precedent dd04486c).
5. **Precedent installs exist.** Large toolchains have landed this way before (go.tgz 66.9MB + full Go tree, 2026-10-27) — "it can't be done here" is a claim that needs a route check against ①–④ first.

## Lane checklist (install/download tasks)

- [ ] Identify the download host; is it whitelisted (card on record)? If unknown, try the exec route and read the failure class.
- [ ] rc23/EPERM + 0-byte + ∅ card ⇒ report per ②, switch to ③ (browser channel) or ④ (GitHub-artifact route) — do not stop at the first failure.
- [ ] Verify the landed artifact (size + checksum/run) before reporting success; a 0-byte file is a failed download, not an install.
