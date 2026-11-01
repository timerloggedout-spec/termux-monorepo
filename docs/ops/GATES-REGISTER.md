# GATES REGISTER — one file · ∀ gated items · separated by gate type

Single-writer: main (9a88e77a). Lanes report gate Δ ↑ one level only; register changes land via PR.
Established 2026-11-01 (owner order). Companion: docs/ops/OWNER-REQUESTS.md (owner asks) — this file = the gate state itself.
Notation: caveman micro dense · states = {CLOSED · OPEN · RESOLVED · TRANSIENT}.

## CARD-BLOCK ‖ ∅ fleet credit card (owner fact 2026-11-01) ⇒ class CLOSED fleet-wide

| item | gate | state | holder |
|---|---|---|---|
| nebius | billing setup mandatory, $0 hold, ∅ skip — signed in ✓ 2026-11-01, ∅ key | CLOSED | provisioning a78e43e6 |
| together | $15 minimum purchase to create keys | CLOSED | provisioning a78e43e6 |
| cerebras | card-gated signup | CLOSED | provisioning a78e43e6 |
| anthropic / openai-codex | pay-first families | CLOSED | provisioning a78e43e6 |
| whatsapp WABA | payment method required | CLOSED | social 628089aa |
| vultr (D2) | payment only post-gift-code ⇒ card-BLOCK (gate D2-NOCARD; $200 gift code first) | CLOSED-at-payment-step | D2 d8f72f94 |
| meta app verification | card option (dual w/ SMS-WALL below) | CLOSED-via-card | social 628089aa |

∀ "owner top-up item" framings RETIRED · ∀ "re-fire on top-up" promises VOID.

## SMS-WALL ‖ phone number ∅ authorized

| item | gate | state | holder |
|---|---|---|---|
| fireworks | phone verification (+1 number + code); account created to that point | OPEN | provisioning a78e43e6 |
| meta developer verification | SMS-capable number ∅ authorized (unblocks meta app + whatsapp number leg) | OPEN | social 628089aa |
| whatsapp | dedicated number ∅ | OPEN | social 628089aa |

## VAULT-GATE ‖ secure entry pending in-lane

| item | gate | state | holder |
|---|---|---|---|
| hyperbolic | google login via vault card (app.hyperbolic.ai) | OPEN | provisioning a78e43e6 |
| unorouter | vault-card login; provider consents pending behind it | OPEN | provisioning a78e43e6 |
| ai21 | vault card in provisioning chat | OPEN | provisioning a78e43e6 |
| devin wiki indexing (DEVINdeepWiki) | owner Devin Settings step: service-user token (IndexOrgRepositories) → secret `DEVIN_API_KEY` + vars `DEVIN_ORG_ID` / `DEVIN_WIKI_EFFORT` | OPEN — blocks continuous automated DEVINdeepWiki refresh; owner manually refreshed repo+branches 2026-11-01 | owner / repo-org ec42d7e8 |
| deepwiki fabric pair | secrets `DEEPWIKI_TOKEN` (mcp.devin.ai probe) + `DEEPWIKI_LLM_API_KEY` (local deepwiki-rs generation — independent provider family, ¬ Cognition) | OPEN | provisioning |
| xfyun | vault card never submitted | OPEN | accounts 79a004f8 |
| tinyfish | TINYFISH_API_KEY vault capture issued; Actions secret = separate step | OPEN | scraping 97b21d62 |

## PROMPT-GATE ‖ 2SV phone prompt (B160V, broken screen) — warn-first rule ∀

| item | gate | state | holder |
|---|---|---|---|
| nebius google prompt | missed AM 2026-11-01 → re-fired 12:46 PT, 89 ✓, email code ✓ | RESOLVED → CARD-BLOCK | provisioning a78e43e6 |
| class rule | prompts land only on B160V; missed = expired; warn-first + instant number relay | STANDING | ∀ lanes |

## CAPACITY-WALL ‖ provider-side, transient

| item | gate | state | holder |
|---|---|---|---|
| jules | session-create refused ×3; entry builds created 3 / completed 0 / errored 3 ⇒ DOWN for entry builds | OPEN | swarm 6628d41d |
| gemini-cli | capacity out (smoke run 41312681504 failed) — repo-story build + interactions-smoke wait on recovery probe | OPEN | swarm 6628d41d |
| deepseek | tunnel down (agent never invoked) | OPEN | swarm 6628d41d |
| qodo | billing-blocked — trial ended (billing class) | OPEN | desk a440bcb2 |

## FUNDED-OUT ‖ key ✓ · balance $0 · permanent absent a card

| item | gate | state | holder |
|---|---|---|---|
| deepinfra · novita · friendli · zai · llm7 · routeway · siliconflow | provisioned + catalog-counted; completions never clear at $0 | CLOSED-class | quota b18fae96 |

## SCOPE-WALL ‖ wired, credential scope/provisioning short

| item | gate | state | holder |
|---|---|---|---|
| huggingface | read token: catalog 200 ✓ · chat 403 ⇒ scope-limited, ¬ missing (harness fix PR #3169) | OPEN | swarm 6628d41d |
| meta | wired-unprovisioned: MODEL_API_KEY / META_API_KEY ∅ provisioned (routes of record #2641) | OPEN | provisioning a78e43e6 |

## DECISION-GATE ‖ owner ruling owed

| item | gate | state | holder |
|---|---|---|---|
| X | parked (owner); data archive download expires 2026-11-06 03:17 PT | OPEN | main |
| modelscope | route ruling | OPEN | provisioning a78e43e6 |
| #1861 | public platform→moniker→handle map direction — HOLD | OPEN | registry ac8e5e6b |
| system-one | blocked-paid ruling | OPEN | main |
| notebooklm | pool-charge ruling | OPEN | quota b18fae96 |
| D5-SPOT | aha spot pending | OPEN | D5 5b1fd8ae |
| D4 kiro id | Kiro ID for 4,000-credit form by 2026-12-01 12:00 PT | OPEN | D4 fefff1ad |
| D3-CLIPS-STORAGE | clips storage gate | OPEN | D3 39fc8b89 |
| AMD onboarding | $100 GPU claim · AMD profile · 1st Academy course (owner-session steps) | OPEN | gates-academy 840bd147 |
| fly.io | support-trial reset sent 2026-10-27; reply pending | OPEN | main |
| github support | Pages-outage ticket draft delivered; filing optional (recovery already happened) | OPEN | email de76e743 |

## EGRESS-WALL ‖ bot-check / reachability

| item | gate | state | holder |
|---|---|---|---|
| kilo | Cloudflare "verify you are human" at app.kilo.ai — owner passes in live tab | OPEN | accounts 79a004f8 |
| approxination.com | hosted arena unreachable at 2026-11-01 check (timeouts, www NXDOMAIN) — claims UNVERIFIED, retry non-gating | TRANSIENT | competitions f6a8a1d9 |
