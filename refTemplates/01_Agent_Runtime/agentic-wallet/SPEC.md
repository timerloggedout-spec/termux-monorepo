# Agentic Wallet — Template Spec

**Schema:** `agentic-wallet-template/v1`
**Status:** registered template (fleet-native; family
`01_Agent_Runtime`). Instantiating this template is a
provisioning act on the established wallet layer — it creates
no new ledger, no new unit, and no new custody.
**Basis:** moneyball DESIGN §11 (wagering schema basis,
layered over §10) ∧ the Swarms concept basis (RESEARCH-6REA7
layered record, Layer 1: per-agent wallet spin-up · balances ·
send/receive · spend controls). Fleet rails differ from the
concept basis where the hard exclusions below say so.

---

## 1. Instantiation target + spin-up

- **Target:** one lane or agent per instantiation
  (`target = {kind: lane|agent, id: <seat/lane/agent id>}`).
- **Spin-up = a provisioning event** on the hash-chained
  wallet-ledger of record (monorepo
  `ops/agentic-gambling/site/wallet-ledger.jsonl`; fold/verify
  via `scripts/moneyball/wallet_ledger.py`, Speculators-build
  custody). A wallet exists exactly when its provisioning
  event is in the ledger and the fold proves it.
- **Genesis rule — cited, not re-derived:** the wallet
  invariant (Addendum 2, moneyball PR #3684: every participant
  has a wallet, required-by-design) ∧ the provisioned set of
  record (WALLETS.json, monorepo PR #4640). Participant
  genesis rides `faucet_issued` events; pool wallets ride
  `pool_provisioned` events at measured-0. An instantiation
  that finds its target already provisioned is a no-op with a
  receipt — never a second genesis.
- **Unit:** `soft_quota_token` (observational). Paper/test
  rails only (see §6).

## 2. Wagering legs

**Core leg (always on) — §11① the ANTE.** Agents are REQUIRED
to wager on QUE tasks; the required form is an **ante per
task**: each agent posts a minimum ante per task, the minimum
**scaled by task complexity**. The complexity class keys off
the **QUE tier / task record of record** — the task's own
recorded complexity is the source, never an agent's
self-assessment. The template records the scaling RULE
(complexity-class → ante band, method-bounded); ante values
are dynamic per Amendment 6 (§5) — ∅ fixed amounts here.

**Optional modules (declared per instantiation):**

| Module | Basis | Shape |
|---|---|---|
| Team-contract fee | §11② | Specific Teams requestable for a % fee per agent contract; the fee is a ledger move from the requester's wallet to the team pool (moniker/role pool classes) |
| Pooled opportunity funding | §11③ | Challenge Opportunities get in-house granted pooled funding (desk-lane pools; `pool:other:pooled-buckets` as the pooled leg); winnings split — a % to the earner ∧ a % to the pool — as ledger events |
| Discounted custom requests | §11④ | Discounted agent-team custom requests; the discount pairs with a bonus of % winnings allocated to the agents, settled as ledger events |
| Algorithm property | §11⑤ | Allocation algorithms are agent property: changeable, sellable, royalty-bearing, customizable. Sale = a ledger transfer between wallets; royalties = residual-stream events back to the author's wallet |

## 3. Spend controls / bounds

Declared parameters (Amendment-6 discipline: the template
declares the parameters; **values are set only at
instantiation, as stamped snapshots** `{value · at · method ·
bounds}` — ∅ fixed values in this template):

- `allowance_cap` — max total outflow per window.
- `per_trade_cap` — max single-move amount.
- `revocable` — the wallet's spend authority is revocable by
  the provisioning lane; revocation is itself a ledger event.

Unset parameters at instantiation read **NOT_ESTABLISHED**,
never a silent default.

## 4. Sweep triggers

Engine of record: `wallet_ledger.py` mode `sweep`
(monorepo PR #4695). Trigger shapes:

- `{threshold ⇒ excess}` — balance above a threshold sweeps
  the excess to the mapped pool.
- `{settlement ⇒ full}` — a settlement event sweeps in full.
- `{manual ⇒ named}` — a named manual instruction sweeps.

Sweeps append paired `sweep_transferred` debit+credit events
and verify in-process, fail-closed. **Threshold values are a
parameter, NOT_ESTABLISHED until ruled** — the engine invents
∅ defaults, and an unruled class never fires.

## 5. % discipline (Amendment 6)

Every % named by a leg (team fee · winnings split · discount ·
bonus · royalties) is DYNAMIC: rules are recorded here;
figures exist only as stamped snapshots
`{value · at · window · method · bounds}` at instantiation or
settlement time. This template asserts ∅ % figure.

## 6. Hard exclusions (stamped in the template)

- ∅ chain/mainnet legs.
- ∅ key custody — the template holds no keys and names no
  key store.
- Real money is a **separate owner gate**: Solana/mainnet
  legs (named in the concept basis) stay behind the
  chain-wiring + key-custody rulings, neither of which this
  template grants or implies.
- ∅ invented balances: a balance renders only as the ledger
  fold proves it.

## 7. Mechanics-on-cards publication

Where an instantiation's agent is also a speculation subject,
its card carries the mechanics block in this shape:

```json
{
  "allocation_algorithm": {
    "id": "<strategy id from the strategies registry>",
    "version": {"value": "<version>", "at": "<stamp>",
                "method": "<how stamped>"} | "NOT_ESTABLISHED"
  },
  "section11_terms": {"change": "...", "sale": "...",
                      "royalty": "..."} | null
}
```

Algorithm version and §11 change/sale/royalty terms render
only as recorded; unrecorded reads NOT_ESTABLISHED / null —
never an invented figure (publication record of reference:
the speculator-instance population registration, 2026-11-03).

## 8. Instantiation procedure

1. Name the target (lane/agent id) and check the provisioned
   set of record — already provisioned ⇒ no-op receipt.
2. Append the provisioning event (genesis per §1) via the
   custodied ledger tooling; verify the fold.
3. Declare spend-control parameters as stamped snapshots
   (§3); leave unruled ones NOT_ESTABLISHED.
4. Enable the optional modules the work needs (§2); record
   the core ante rule reference (complexity source = the QUE
   tier / task record).
5. Configure sweep triggers (§4) with threshold values only
   where a ruling exists.
6. Receipts: the instantiation receipt names
   {target · provisioning event seq · parameters as stamped ·
   modules enabled · exclusions acknowledged}.

## 9. Claims ceiling

This template describes mechanics shapes and provisioning
procedure only. It asserts no balances, no % figures, no
threshold values, and no chain capability. Where a fact is
unruled or unrecorded, the template's word is
NOT_ESTABLISHED.
