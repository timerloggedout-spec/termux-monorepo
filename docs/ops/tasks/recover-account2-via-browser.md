# Task: recover account-2 bearer via browser automation

The prior automation lives in `deepseek-cli/*.cjs`. The profile
`browser-data-account2-clean` is the most recent used state. The
token was extracted to `token_account2.txt` — but that file now
holds account-1's value, meaning a prior run captured the wrong
account or was later overwritten.

## Goal

Produce a **fresh** `~/.deepcli/account2.env` with a 64-char bearer
whose sha256 prefix is **distinct from account-1** (`78088cb5…`).

## Steps

1. Verify `chromium-browser` and `puppeteer` are present:
       test -x /data/data/com.termux/files/usr/bin/chromium-browser
       ls ~/deepseek-cli/node_modules/puppeteer

2. Run the existing extractor with the clean profile:
       cd ~/deepseek-cli
       node extract-2nd-token.cjs

   This launches chromium (headless), loads the profile, and prints
   `TOKEN CAPTURED: <prefix>` when a Bearer is seen on an API request.

3. If no token is captured in 60s, the browser profile lost its
   session. Then:
   - Launch chromium-browser with `--user-data-dir=browser-data-account2`
   - Navigate to `chat.deepseek.com/login`
   - Sign in as account-2 (HITL once: type password; Gmail code
     verification is automated via the existing Gmail tooling)
   - Send one message in the web UI to force the API call
   - extract-2nd-token.cjs (background listener) captures the Bearer

4. Write the captured token to `~/.deepcli/account2.env`:
       DEEPSEEK_TOKEN_SECONDARY='<64-char ors…>'
       DEEPSEEK_ACCOUNT_2='<same>'
       DEEPSEEK_COOKIES_2='<path to cookies_2.json>'

5. Verify with:
       python3 -c "import sys,pathlib;sys.path.insert(0,str(pathlib.Path.home()/'deepcli'));\
         from session_manager import get_new_session;\
         s=get_new_session('secondary'); print(s['account'], len(s['token']))"

   Must print `secondary 64`.

6. Confirmation: `verify-session.py secondary <uuid>` on a known
   account-2 session id from `cookies_2.json` context returns 200.

## HITL boundary

Only the login form typing is HITL (once). Everything else —
profile launch, cookie injection, token intercept, file write,
git commit — is automated.

## Invariant

- Never overwrite `config.json` (account-1) or `config-2.json`
  until the new bearer's sha differs from account-1's.
- Keep `token_account2.txt.bak` untouched (branch retention doctrine
  applies to files too).
- Log the resulting token's sha to `~/.deepcli/logs/hygiene/key-rotation.jsonl`
  (value masked, only sha + length).
