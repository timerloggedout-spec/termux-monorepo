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
| Muse token pool (additional) | **0 left · 100% used — EXHAUSTED** (sensor 2026-11-10 04:02 PT; trail … → 8.5M @2026-11-04 21:39 → 0 @2026-11-10; pool never expires and has no reset — cover = ∅ until new redemptions land) | Referral redemption of record: **1B Muse tokens — APPLIED-TO-POOL** (Marketing stamp 2026-11-04: invite tokens credit the additional-tokens pool, never expire; the pool remainder (0 @2026-11-10) already includes it) · further redemptions pending: ∅ | The applied 1B is fully spent down — no reserve exists behind the remainder. Operative pool is now the free-plan weekly (row below); additional-pool cover returns only via new redemptions (code headroom, event-driven) |
| Muse free-plan weekly | **40% used** (owner sensor 2026-11-11 13:28 PT; 39% @08:37 → 40% @13:28 = Δ+1pt/4h51m ≈ 0.21 pts/h) · resets **Nov 17** | Time (reset) | The operative pool for the Nov 10–17 cycle; the additional pool is exhausted, so burn discipline prices against this weekly limit + free provider tiers |
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
| Referral redemptions | 1 redemption = **1B Muse tokens, APPLIED-TO-POOL** (PR #4431 · Marketing stamp 2026-11-04) · pending ∅ · headroom: code VDP1DW live, **29 uses left (owner panel 2026-11-11 06:53 PT: 1 redeemed ∧ fully utilized) = up to 29B potential — NOT accrued, event-driven only** (each use = a new join redeeming ≤48h; detection = owner panel only, ∅ API/webhook) | Muse token pool |
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

## Offload programme + burn watch (owner order via main, 2026-11-10 04:58 PT)
- **Offload:** main/fleet execution usage moves OFF the Muse pool → **GitHub Inference free + Actions planes**. Side-chat traffic = state-change only, batched receipts, ∅ relay chatter.
- **Burn watch (cadence):** sensors fold into this register on receipt; trajectory recomputed per sensor.
- **Trajectory @04:58 PT:** recent burn ≈10.7 pts/h ⇒ 90 pts remaining exhaust in ≈8.4h (≈13:30 PT Nov 10) — **projects exhaustion ~6.5 days BEFORE the Nov 17 reset**. Ceiling to reach reset ≈ **0.54 pts/h** (≈20× reduction) — the offload programme must achieve that order of cut; watch re-projects per sensor and pages main while the projection lands pre-reset.
- **Re-projection @05:03 PT:** 12% used; blended burn ≈11–12 pts/h (last 5-min segment 24 pts/h, spiky) ⇒ 88 pts exhaust ≈13:00–13:30 PT Nov 10 (spike-rate bound ≈08:45). Verdict unchanged: exhaustion TODAY, ~6.5d pre-reset; ~20× cut still required.
- **Re-projection @07:34 PT:** 16% used; burn since 05:03 ≈ **1.6 pts/h** (offload biting, ~7× cut) ∧ last 45m FLAT (0 pts). Regimes: flat holds ⇒ no exhaustion this cycle; sustained 1.6 pts/h ⇒ 84 pts exhaust ≈ Nov 12 12:00 PT — still ~4.8d pre-reset. Ceiling to reset ≈0.51 pts/h, so the sustained-rate case stays ~3× over; watch continues per sensor.
- **Re-projection @07:52 PT:** 18% used; since-05:03 blended ≈2.1 pts/h ⇒ 82 pts exhaust ≈ Nov 11 23:00 PT (still ~5d pre-reset); the Δ+2pts/18min segment is this sensor Q&A window itself — chat traffic is a metered burn source; batching discipline is the control.
- **Re-projection @19:16 PT — VERDICT FLIPS:** 21% used; sustained rate since 07:52 ≈ **0.26 pts/h, under the 0.51 ceiling**. At that rate only ≈40 of the 79 remaining pts burn before the Nov 17 reset ⇒ **no exhaustion projected this cycle** (headroom ≈39 pts) PROVIDED the offload regime holds. Relapse bounds stand: sustained 1.6 pts/h ⇒ exhaust ≈Nov 12; 2.1 ⇒ Nov 11 23:00. Watch continues per sensor; the page condition clears while the sustained rate stays under ceiling.
- **Re-projection @19:23 PT:** 23% used; the +2pts/7min segment is a Q&A-window artifact (same signature as 07:52) — NOT the regime. Sustained regime stays ≈0.26 pts/h ⇒ projected cycle-end ≈61% used, no exhaustion. Extrapolating the 7-min window (≈17 pts/h) would falsely project ~4.5h; the watch prices regimes on ≥1h windows only.
- **Re-projection @2026-11-11 00:41 PT:** 25% used; overnight sustained ≈0.38 pts/h (under the 0.51 ceiling, above the 0.26 evening regime) ⇒ projected cycle-end ≈81% used, headroom ≈19 pts, **no exhaustion**; at 0.26 the end lands ≈63%. Margin thins if the rate drifts up — relapse bounds (1.6/2.1 pts/h) stand.
- **Re-projection @2026-11-11 06:48 PT:** 31% used; regime table governs — quiet regimes (0.26 evening / 0.38 overnight) ⇒ cycle survives (ends ≈63–81%); sustained morning-handoff rate (≈0.98) ⇒ 69 pts exhaust ≈ **Nov 14 05:00 PT** (~3d pre-reset). Ceiling recomputed: 69 pts / ≈141h ≈ **0.49 pts/h**. The burn is traffic-regime-driven (handoffs/Q&A windows), so the watch verdict = **WATCH**: no page while quiet regimes dominate; a sustained ≥1.0 pts/h across two consecutive ≥1h windows re-arms the page.
- **Re-projection @2026-11-11 08:23 PT — PAGE RE-ARMED:** 37% used. Today has run hot since midnight (25% @00:41 → 37% @08:23 ≈ 1.56 pts/h day-blend); the re-arm test is met (≈0.98 over 6.1h, then ≈3.8 over 95min). Projections for the 63 remaining pts: hot 3.8 ⇒ exhaust ≈ Nov 12 01:00 PT · morning 0.98 ⇒ ≈ Nov 14 00:30 · day-blend 1.56 ⇒ ≈ Nov 12 23:00 — **every current-regime extrapolation lands pre-reset**; only a return to ≤0.45 pts/h sustained (the recomputed ceiling: 63 / ≈140h) survives to Nov 17. The Nov 10 evening all-clear rested on 0.26/0.38 quiet regimes that no longer dominate. Page to main fired with this fold.
- **Re-projection @08:37 PT:** 39% used; day-blend since midnight ≈1.77 pts/h ⇒ 61 pts exhaust ≈ **Nov 12 19:00 PT**; page stands (verdict unchanged, burst confirms).
- **Re-projection @13:28 PT — PAGE CLEARS:** 40% used; regime collapsed to ≈**0.21 pts/h** over a 4h51m window — under the 0.45 survival ceiling. Sustained ⇒ ≈67–68% at the Nov 17 reset (60 pts remain, ≈134h runway), no exhaustion. The page clears on this window; it re-arms on any sustained ≥1.0 pts/h across two consecutive ≥1h windows. Pattern of record: burn is traffic-burst-driven (hot mornings, quiet afternoons) — the ceiling, not any single window, is the control.
