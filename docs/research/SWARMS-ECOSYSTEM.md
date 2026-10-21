# Kye Gomez’s Swarms in the Termux monorepo

The intended person is **[Kye Gomez (`kyegomez`)](https://github.com/kyegomez)**. His profile identifies him as the founder of Swarms and pins [`kyegomez/swarms`](https://github.com/kyegomez/swarms), the Python multi-agent orchestration framework. The integration already pins that correct upstream. The previous repository inventory, however, targeted `timerloggedout-spec`; it was not an inventory of Kye Gomez’s work. This continuation corrects that mistake without discarding historical evidence.

## What the corrected inventory found

The [Kye Gomez public-repository inventory](swarms-kyegomez-repositories.json) contains **455 repositories across five successful GitHub API pages**, with no duplicate records or collection errors. The collector follows pagination to exhaustion and checks every returned repository’s owner against `kyegomez`. “Exhaustive” describes the public listing returned during collection, not private repositories, every organization he contributes to, code-search results, or a source audit.

Name/description matching produced **19 Swarms/multi-agent leads** and **197 model-research leads**. These are discovery groups, not findings that all such projects integrate with Swarms or work on Android. The full listing includes repositories outside both groups. Reproduce the collection explicitly with:

```sh
python3 scripts/swarms/inventory.py --owner kyegomez \
  --output docs/research/swarms-kyegomez-repositories.json
```

| Group | Kye-owned examples | What is established |
|---|---|---|
| Main orchestration | [`swarms`](https://github.com/kyegomez/swarms) | Correct upstream; selected implementation paths inspected at the pinned revision. |
| Documentation/service leads | [`swarms-docs`](https://github.com/kyegomez/swarms-docs), [`swarms-marketplace-api`](https://github.com/kyegomez/swarms-marketplace-api), [`swarms-home`](https://github.com/kyegomez/swarms-home) | Public repository identities and metadata, not verified deployed services. |
| Multi-agent research | [`awesome-multi-agent-papers`](https://github.com/kyegomez/awesome-multi-agent-papers), [`SwarmLogic`](https://github.com/kyegomez/SwarmLogic) | Reading/research leads, not blanket runtime recommendations. |
| Model/algorithm research | [`swarms-pytorch`](https://github.com/kyegomez/swarms-pytorch), [`zeta`](https://github.com/kyegomez/zeta), [`MultiModalMamba`](https://github.com/kyegomez/MultiModalMamba), [`MambaTransformer`](https://github.com/kyegomez/MambaTransformer) | Separate model/algorithm projects, not interchangeable orchestration runtimes. |

The earlier [`swarms-user-repositories.json`](swarms-user-repositories.json) is retained unchanged: **676 public `timerloggedout-spec` repositories and 241 metadata candidates**. That inventory can help map the monorepo owner’s adjacent projects, but it does not answer the Kye Gomez inventory question. Neither inventory constitutes inspection of every repository’s code.

## The exact catalog page supplied

The [Arnon-hs catalog card at the supplied commit](https://github.com/Arnon-hs/open-source/blob/a8d1c0ca86d773b93a0ae8049eff33e12e58fa3e/orchestration/kyegomez-swarms.md?plain=1) explicitly names **`kyegomez/swarms`**. It is a valid discovery lead for the intended target. Its 74/100 score, 6.6k-star summary, and “Medium” readiness label are third-party catalog judgments, not build/test results or Android certification. The card itself says dependencies, license, security posture, and maintainers need review. Its push/update/discovery dates refer to different observations; do not treat them as one current maintenance measurement.

The [catalog’s own trust boundary](https://github.com/Arnon-hs/open-source#trust-boundary) calls its scores discovery aids, not endorsements or security guarantees. The primary GitHub repository page displayed 5,518 commits when read; a commit count is not source code reviewed. This work inspects selected implementation paths rather than claiming to audit that history or thousands of code-search matches.

## What the actual Python source supports

The canonical shallow reference at `refTemplates/smods/swarms` is pinned to [`8ec7948ce6e8ab28c4454d6c2c3187a735672067`](https://github.com/kyegomez/swarms/commit/8ec7948ce6e8ab28c4454d6c2c3187a735672067). Its [manifest](https://github.com/kyegomez/swarms/blob/8ec7948ce6e8ab28c4454d6c2c3187a735672067/pyproject.toml#L6-L83) declares `swarms` 16.0.2, Apache-2.0, Python `>=3.10,<4.0`, and a Beta classifier. Most dependencies are unconstrained; the source pin is not a transitive dependency lock.

At that revision, the tracked tree contains 1,251 files, including 1,020 Python files; 212 Python files under `swarms/` total 72,768 physical lines. These measurements describe size, **not audit coverage**. The [focused source review](SWARMS-CODE-REVIEW.md) separates confirmed implementation details from runtime claims.

The optional adapter uses real `Agent` and `SequentialWorkflow`, forwards validated conversation messages through the existing model hub, and grants no tools, MCP endpoints, shell access, or automatic Git changes. The SDK test passes with deterministic stub inference and network connections forbidden. That proves the selected Linux orchestration path, not provider quality or Android support.

Two upstream behaviors justify isolation: [telemetry is enabled by default](https://github.com/kyegomez/swarms/blob/8ec7948ce6e8ab28c4454d6c2c3187a735672067/swarms/telemetry/otel.py#L46-L69), and initialization has process/workspace side effects. The adapter opts out before import and uses a temporary workspace. Prefer its standalone CLI over embedding in an unrelated multithreaded host.

## Rust and remote services are valid options

**Python-only, phone-only execution is not a requirement.** The user explicitly accepts Rust and already uses remote services. [`The-Swarm-Corporation/swarms-rs`](https://github.com/The-Swarm-Corporation/swarms-rs) is therefore a first-class evaluation candidate, not ruled out by the Python adapter. See the [Rust assessment](SWARMS-RUST.md) for pinned source findings and the existing hub interface.

Keep three choices separate: native Termux orchestration with remote inference; remote Linux orchestration with remote inference; and local model execution. Remote inference avoids requiring model weights/GPU libraries on the phone. Remote Linux orchestration can also avoid Android-native build requirements. Neither proves Android builds or authorizes public device exposure or bypassing `hub_mcp` permissions.

## Adjacent organization projects

The Swarm Corporation organization is a separate namespace from Kye’s personal listing. Previously read manifests identify [`swarms-tools`](https://github.com/The-Swarm-Corporation/swarms-tools) (MIT, Python `^3.10`, including `orjson`/`lxml`), [`swarm-models`](https://github.com/The-Swarm-Corporation/swarm-models) (MIT, Python `^3.10`, model dependencies), and [`swarms-memory`](https://github.com/The-Swarm-Corporation/swarms-memory) (MIT, Python `^3.10`, multiple heavyweight memory backends). These are optional candidates, not mandatory installations. Native extensions/local ML stacks need target-specific validation; remote services may be a better fit.

## Applied here

The [architecture synthesis](../architecture/SWARMS-SYNTHESIS.md), [optional integration](../../integrations/swarms/README.md), and [validation record](../../integrations/swarms/VALIDATION.md) remain implementation entry points. This continuation corrects provenance, adds a reproducible owner-checked collector and offline tests, and records selected Python/Rust source evidence. It does not claim all-code coverage, native Termux success, a live deployment, or measured performance improvement.
