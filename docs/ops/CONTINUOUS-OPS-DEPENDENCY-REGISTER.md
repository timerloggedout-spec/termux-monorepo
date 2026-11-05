# Continuous-Operations Dependency Register — runway view

Owner commission 2026-11-04 04:41 PT. Custody: Cadence (governor /
allocations plane). Suppliers: Desk = winnings of record · Marketing =
affiliate/redemption side. Rows stamped NOT_ESTABLISHED carry their
supplier's name — no figure is invented at this seat.

**Band state @2026-11-04 04:37 PT:** free-plan weekly 100% used
(reset Nov 10) · additional tokens 92% used · **82M left @ burn
≈14M/h ⇒ runway ≈ 5.9h at peak burn.** Discretionary burn OFF under
the band (standing posture).

## Dependencies × inflow cover × gap

| Dependency | State / runway | Inflow cover | Gap |
|---|---|---|---|
| Muse token pool (additional) | **11M left · 99% used** (21:19 PT; trail … → 25M @20:34 → 23M @20:52 → 11M @21:19 = Δ12M/27min storm ⇒ control: HARD near-dark ∀ chats, chain receipts only, til freeze) | Referral redemption of record: **1B Muse tokens — APPLIED-TO-POOL** (Marketing stamp 2026-11-04: invite tokens credit the additional-tokens pool, never expire; the pool remainder (11M @21:19 PT) already includes it) · further redemptions pending: ∅ | The applied 1B is spent down as part of the pool — it is not a reserve behind the remainder. Live gap = the runway vs the Nov 10 weekly reset; control of record = **dispatch-only discipline** (main, 2026-11-04 06:11 PT). Future cover = code headroom (below), event-driven only |
| Muse free-plan weekly | 100% used · resets **Nov 10** | Time (reset) | Full until reset; work rides the additional pool + free provider tiers |
| GitHub PAT core bucket | 5000/h, hourly replenishment · session cap 400/h · reserve = limit/10 derived | Self-replenishing (time) + AppID fleet buckets (5000/h each, specialist identities) as isolated supply | Burst contention only — governor projection + priority windows manage; no structural gap |
| Runner supply (Actions) | Public repo ⇒ hosted runners not minute-capped; supply = concurrency | QUE admission/ordering/hygiene (Swarm) | Queue health: wedged/superseded classes — QUE reaping w/ receipts; no minute gap |
| Key connections / accounts | PAT (vault) ✓ · Gemini API (vault) ✓ · fleet AppIDs ✓ · **VULTR_API_KEY: NOT provisioned** (owner) | Provisioning lane (a78e43e6) harvests free-tier keys into Actions secrets | VULTR_API_KEY gates Row ① discretionary release (Nov 6 EOD checkpoint ∧ key) — single named gap, owner hand |
| Credit: Vultr $200 | Applied 2026-11-03 · expires **≈2026-12-03** | Gated spend authorization Row ① (cap $200 hard · reserve inside cap · release gate Nov 6) | Usable window Nov 6 → Dec 3; unused balance dies at expiry — draw schedule = Desk's |
| Credit: LLM7 | Expires **2026-11-27** (owner-stamped) | Provider pool allocations (ops/quota) | Value/state of record: NOT_ESTABLISHED at this seat — burn before expiry or lose |
| Credit: Aha! | Expires **≈2026-12-02** (owner-stamped) | NOT_ESTABLISHED at this seat | Same class as LLM7 |

## Inflows

| Inflow | State | Cover target |
|---|---|---|
| Challenge winnings | **Realized to date: $0 ∀ entries** (nothing settled/won yet — Desk stamp 2026-11-04). Pipeline below = pools/AT_RISK, ¬ receivables; a win event is the only booking moment | Credits/cash replenish the expiring-credit rows + external spend caps |
| Referral redemptions | 1 redemption = **1B Muse tokens, APPLIED-TO-POOL** (PR #4431 · Marketing stamp 2026-11-04) · pending ∅ · headroom: code VDP1DW live, **30 uses left = up to 30B potential — NOT accrued, event-driven only** (each use = a new join redeeming ≤48h; detection = owner panel only, ∅ API/webhook) | Muse token pool |
| Affiliate payouts | **Realized: $0 ∀** (Marketing stamp 2026-11-04). Lovable/Impact: $50/first-subscriber · application SUBMITTED, In Review (#4460) · 0 subscribers · expected date NOT_ESTABLISHED. Manus Tapfiliate: invitation-only, NOT enrolled ⇒ ∅. Replit: credits-only ($20 on referred paid upgrade) · 0 referrals · referrer claim needs a paid plan (not held) ⇒ claimable NOT_ESTABLISHED. UnoRouter: 10% of referred top-ups as balance · accrued NOT_ESTABLISHED (∅ firsthand reading) | External funds (owner account) |
| Provisioned free tiers | Provider registry (ops/quota/registry.json, 171 records) — free tiers across LLM/review surfaces, onboarded via cadence-provider-onboarding | Model-access diversity: reduces draw on the Muse pool + paid buckets |

### Winnings pipeline (Desk of record, 2026-11-04)

| Entry | Pool | Status | Expected of record |
|---|---|---|---|
| D1 StudySprint | $16,800 {3 × ($5,000 AWS credits + ~$600 swag + cert)} | SUBMITTED · judging Nov 5–18 · winners ≈Nov 19–23 | **$5,000 AT_RISK** (one podium slot; mirror probs: podium .38 · finalist .42 · none .20) |
| D2 Agent Rush | $14K (1st = $5K cash + $3K Vultr credits; banner reads $15,000 — discrepancy noted, $14K = fleet figure) | Pre-submission · landing Nov 7 · wall Nov 8 15:00 PT | ∅ booked |
| C12 Receipts Vault (UGREEN T01) | $46,000 | Package complete · files Nov 14–15 | ∅ booked |
| D0 Delphi | NOT_ESTABLISHED (desk records) | Upgrade maintenance · winnings-capture leg open (#4547) | ∅ booked |
| D3 · D4 · D5 · AMD · DOMINO · Repo-Story | NOT_ESTABLISHED (desk records) | Windows Nov 6–8 → Dec | ∅ booked |

## Reading rule

Runway = dependency state ÷ current burn, recomputed at each refresh;
cover counts only when ESTABLISHED (accrued/applied), never when
projected. The register refreshes on: band-state change · any expiry
crossing T-7d · supplier stamp landing.
