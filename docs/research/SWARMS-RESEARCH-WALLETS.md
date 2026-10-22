# Swarms research and wallet lanes (THUB-016)

This is a **planning-only** source registry and offline planner. Canonical parity work targets the Python [`kyegomez/swarms`](../../integrations/swarms/source-lock.json) source lock; Rust [`swarms-rs`](../../integrations/swarms/rust/Cargo.toml) is a parallel primary/testing alternative. AdvancedResearch is the likely intended research repository, not a definitive identification. Registering sources does not mean any upstream runtime has been integrated.

## Offline plan CLI

```sh
python3 scripts/swarms/research-plan.py --lane parity --task 'Compare agent orchestration contracts'
python3 scripts/swarms/research-plan.py --lane research --task 'Assess research-agent boundedness'
python3 scripts/swarms/research-plan.py --lane wallets --task 'Review paper CSV accounting'
```

The standard-library-only command emits deterministic JSON with `status: planned`, exact pinned revisions, the existing market-contract path, and evidence requirements. It rejects blank tasks and tasks longer than 500 characters. There is intentionally **no execute mode**, no upstream imports, no network/RPC calls, and no secret access. A plan is not evidence of work completed. Python source-file SHA-256 values are recorded in `integrations/swarms/research-lanes.json` from the existing source lock; Rust's revision is pinned in `Cargo.toml`.

## Research source and review boundaries

AdvancedResearch is pinned at `a262cb9d9703681c5a5066f03eb9fb89ad4d9cae`. At that revision, [`advanced_research/main.py`](https://github.com/The-Swarm-Corporation/AdvancedResearch/blob/a262cb9d9703681c5a5066f03eb9fb89ad4d9cae/advanced_research/main.py) uses Swarms `Agent`, `Conversation`, and `exa_search`, globally loads dotenv, defaults to GPT/Claude, uses `ThreadPoolExecutor(os.cpu_count)`, permits unbounded queries, and yields `as_completed` ordering. Its [manifest](https://github.com/The-Swarm-Corporation/AdvancedResearch/blob/a262cb9d9703681c5a5066f03eb9fb89ad4d9cae/pyproject.toml) declares MIT, Python >=3.10, and unconstrained `swarms`, `swarms-tools`, and `orjson` dependencies. Any future design needs explicit bounded concurrency/query/input limits, deterministic collection if desired, a secret-loading policy, and pinned dependency treatment before considering execution. README claims of 90.2% performance improvement are not measured or validated here.

## Paper wallets are the implementation target

The owner clarified that wallets mean **paper `.csv` accounting**, not an on-chain adapter for a swarm deployment. MSM-012 exports existing MSM-005 market snapshots into paper-only stake/card/offer rows. The CSV is a disposable projection, not a second ledger, funded wallet, account balance, quota reservation, or settlement authority. No RPC, private key, signer, treasury, or payment execution is added.

```sh
python3 -m scripts.model_selection_market.market --demo > /tmp/market-snapshot.json
python3 -m scripts.model_selection_market.paper_wallet export /tmp/market-snapshot.json /tmp/paper-wallet.csv
python3 -m scripts.model_selection_market.paper_wallet view /tmp/paper-wallet.csv
```

Kye Gomez Research/framework integration remains an assigned task; a paper export does not complete it. The AdvancedResearch source below is still a research candidate, not an integrated runtime. See the [current wiring audit](../../integrations/swarms/OPERATING-STATUS.md).

## Historical chain/payment research boundaries

The source registry pins ATP `fc4940f145f38529b9acf5c9e79b0435ab769b7f` and `kyegomez-swarms-token-usecases` `25e66b156d70a6ff32735449876609a2ec91b3c0`. [ATP configuration defaults](https://github.com/The-Swarm-Corporation/ATP-Protocol/blob/fc4940f145f38529b9acf5c9e79b0435ab769b7f/atp/config.py) include mainnet-beta and the mainnet USDC mint, plus treasury/hosted settlement concepts. Example private-key headers are **not** a safe custody pattern. No wallet or payment path is authorized to execute transactions. Any future readiness review must establish explicit RPC chain and genesis identity, test mint, allowlisted recipients and treasury, signer separation, caps, replay protections, and escrow/refund invariants. These controls apply only if chain integration is separately requested later; they are not prerequisites for the paper-wallet or Research framework work. The [Swarms x402 example](https://docs.swarms.world/examples/integrations/x402-payment) is a separate reference and documents Base Sepolia; it does not authorize wallet execution.

The token-usecases repository has only three commits: its [README](https://github.com/The-Swarm-Corporation/kyegomez-swarms-token-usecases/blob/25e66b156d70a6ff32735449876609a2ec91b3c0/README.md) describes wallets, auctions, staking and a token economy, while [`main.py`](https://github.com/The-Swarm-Corporation/kyegomez-swarms-token-usecases/blob/25e66b156d70a6ff32735449876609a2ec91b3c0/main.py) loads YAML agents and calls Groq, not wallet settlement. Treat those token concepts as research leads, not implemented wallet/payment functionality.

## Existing market authority

Bids, wagers, and offers already belong to MSM-005 in [`DESIGN.md`](../proposals/active/model-selection-market/DESIGN.md#6-bets--wagers--bids-itself--others--job-msm-005), implemented by [`market.py`](../../scripts/model_selection_market/market.py). Continue its observational, free-only policy and existing ledger; do **not** create a second ledger. Market events remain ledgered and observational until two observe cycles plus a ledger decision; no automatic paid spend.
