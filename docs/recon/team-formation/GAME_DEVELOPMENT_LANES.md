# Game Development & Autonomous Production Lanes

**Status:** additive design and intake implementation; specialist cohort evolution remains DoE-governed.  
**Seed:** [Issue #243 — Game Teams](https://github.com/timerloggedout-spec/termux-monorepo/issues/243).  
**Related contracts:** [Game Player Fleet](./GAME_PLAYER_FLEET.md), [Roster Context Schema](./ROSTER_CONTEXT_SCHEMA.md), [Issue Template Dispatch](../../ops/ISSUE-TEMPLATE-DISPATCH.md), [DoE Family](../../ops/DOE-FAMILY.md).

## 1. Boundary and operating model

Game Development is a first-class build lane. It is not the Game Player Fleet and it is not Game QA.

| Lane | Owns | Does not own |
|---|---|---|
| **Game Development & Production** | Game design, code, engine/runtime, assets, tools, integration, builds, developer automation. | Independent QA verdicts; player-fleet performance scoring; its own release approval. |
| **Game Player Machines & Genre Teams** | Approved gameplay sessions, scenario execution, player/agent behavior, telemetry and reset evidence. | Game implementation or developer scorecards. |
| **Game QA & Accessibility** | Independent reproduction, functional/compatibility/accessibility verification, regression verdicts. | Self-certification of the implementation it reviews. |
| **Game ML Research** | Controlled evaluation of policies, vision, planning, simulation, learning algorithms and game-playing stacks. | Treating a research score as proof of production readiness. |
| **Reverse Engineering / Interoperability** | Authorized artifact and protocol understanding, compatibility analysis, toolchain taxonomy and evidence. | DRM/anti-cheat circumvention, unauthorized access, cracking, warez or exploitation of third-party targets. |
| **DoE / Specialist Pool Governance** | Experiment design, candidate cohorts, configured-instance measurement, generational selection, review and lineage. | Granting access or permissions through a score. |

The separation is deliberate: **developers build; player agents play; QA verifies; research evaluates; DoE measures and improves the specialist population.**

## 2. Nested intake decisions

Resolve these decisions in order. A later choice must not silently override an earlier constraint.

```text
INTENT
 ├─ create a game / prototype
 ├─ implement a feature or repair a defect
 ├─ port, migrate, mod or extend an authorized project
 ├─ build engine, editor, asset or developer tooling
 └─ research prototype / benchmark
      ↓
PROJECT + AUTHORITY
 ├─ owned / internal
 ├─ open source (license recorded)
 ├─ explicit written authorization (reference recorded)
 └─ otherwise → stop / research-only
      ↓
GAME SHAPE
 ├─ 2D / 2.5D / 3D / mixed
 ├─ single-player / co-op / competitive / asynchronous
 ├─ real-time / turn-based / simulation / interactive narrative
 └─ genre facets (not mutually exclusive)
      ↓
PLATFORM + ENGINE
 ├─ web / Android / iOS / desktop / VR-AR / authorized console
 ├─ existing engine? → preserve its version and conventions
 └─ new project? → choose by target, team capability, license and build path
      ↓
SPECIALIST CONTEXTS
 ├─ game design & systems
 ├─ gameplay / AI / navigation
 ├─ engine / runtime / architecture
 ├─ graphics / rendering / shaders
 ├─ 2D art / 3D art / animation
 ├─ audio / UI-UX / accessibility
 ├─ physics / simulation / networking
 ├─ tools / asset pipeline / build & release
 ├─ performance / platform integration
 └─ ML / telemetry / interoperability
      ↓
TOOL PROFILE + WORK PACKAGES
 ├─ tool versions, licenses, capabilities, availability
 ├─ dependencies and exclusive file ownership
 └─ parallelize only independent packages
      ↓
BUILD → EXECUTE → VERIFY → REVIEW → INTEGRATE
      ↓
DoE records outcome → cohort review → versioned improvement
```

### Classification dimensions

- **Project kind:** new game, prototype, feature, bug fix, port, migration, mod/extension, engine/tooling, research prototype.
- **Game shape:** 2D, 2.5D, 3D, mixed; single-player, co-op, competitive, asynchronous; real-time, turn-based, simulation, narrative.
- **Genre facets:** strategy/4X, action/arcade, RPG/adventure, simulation/builder, puzzle/educational, racing/sports, sandbox/survival, roguelike/procedural, multiplayer/cooperative/competitive.
- **Platform:** browser, Android, iOS, Linux, Windows, macOS, VR/AR, or explicitly authorized console targets.
- **Engine/framework:** existing engine first; new selection only after the project constraints and build/test path are known.
- **Specialist context:** one accountable owner per work package; supporting specialists are separately named and scoped.

Genre is a **facet**, not a fixed team identity. A strategy game can need networking, accessibility, rendering and build specialists at the same time.

## 3. Engine and framework selection

| Candidate | Best-fit context | Agent/tool integration | Important boundary |
|---|---|---|---|
| **Godot 4** | Open-source 2D/3D, desktop/mobile, rapid prototypes. | Editor CLI, headless import/export, GdUnit4 CLI tests. | Pin engine/export-template versions; graphical checks still need a render-capable runner. |
| **Unity 6+** | Broad 2D/3D/mobile/VR production and established asset ecosystems. | Unity CLI, official agent skills and MCP mode; editor automation. | Unity's MCP mode requires Unity 6+; licenses and package versions must be recorded. |
| **Unreal Engine 5** | High-fidelity 3D, complex worlds, C++/Blueprint workflows. | Unreal Automation Framework, commandlets, Python/editor scripting where supported. | Large resource footprint; schedule heavy builds/renders on remote runners. |
| **Phaser 4** | 2D browser games, playables and web-first experiences. | JavaScript/TypeScript, npm/pnpm/bun scaffolds, browser automation. | Phaser is 2D; use another engine/library for full 3D or console-native targets. |
| **Custom/runtime-specific** | Existing project or constrained embedded/experimental target. | Existing build/test scripts and explicit adapters. | Do not introduce a new engine solely to satisfy a generic agent preference. |

Selection is evidence-based. The intake records the chosen engine and version, alternatives considered, target platform, licensing, export path, CI runner needs and migration risk. The repository does not assume an engine is installed because it appears in this table.

## 4. Specialist contexts and matched tooling

Tool names below are candidate tool profiles. A task must resolve each selected tool to a versioned, reviewed profile before execution.

| Specialist context | Work owned | Tooling candidates | Minimum verification |
|---|---|---|---|
| **Game Design & Systems** | GDD, mechanics, core loop, progression, economy, balance, narrative and acceptance contracts. | Markdown/YAML/JSON GDD; Mermaid; spreadsheet/CSV analysis; engine data resources. | Requirement-to-feature traceability; rule consistency; deterministic examples. |
| **Gameplay Engineering** | Input, movement, combat, inventory, quests, interaction, state machines and save/load. | Engine-native scripting/C++; Godot/Unity/Unreal debugging; pytest or engine unit tests. | Unit/scenario tests; save/load invariants; replayable defect reproduction. |
| **Engine & Runtime Architecture** | Scenes, ECS, resource lifecycle, scripting, serialization, plugins and runtime boundaries. | Godot CLI; Unity CLI/MCP; Unreal commandlets/Automation; CMake for native components. | Clean import/build; API/serialization tests; lifecycle and migration tests. |
| **Graphics & Rendering** | Materials, shaders, lighting, cameras, render pipeline and visual effects. | Shader languages; Shader Graph; RenderDoc; PIX; GPU captures. | Shader compile; render captures; visual regression and frame-budget evidence. |
| **2D Art & UI Assets** | Sprites, tiles, icons, atlases, UI assets and image processing. | Krita; Aseprite/LibreSprite; ImageMagick; TexturePacker or engine atlas tools. | Dimensions/alpha/atlas checks; asset references resolve; visual review. |
| **3D Art & Environment** | Meshes, materials, scenes, environment assembly, import/export. | Blender + Python API/background mode; glTF tooling; mesh validators. | Batch export; scale/orientation/material checks; target-engine import proof. |
| **Animation & Rigging** | Skeletons, retargeting, clips, blend trees and animation state. | Blender; engine animation graph/state-machine tools; glTF animation. | Skeleton/clip integrity; transition tests; in-engine capture. |
| **Audio Engineering** | SFX, music integration, spatial audio, buses, mixing and runtime audio. | Audacity; FFmpeg; engine audio; FMOD/Wwise when license and project fit are verified. | Format/sample-rate checks; event/bus resolution; runtime playback and mix review. |
| **Physics & Simulation** | Collision, rigid bodies, vehicles, navigation constraints and simulation. | Engine physics; Box2D/Jolt/Bullet where suitable; deterministic simulation harnesses. | Fixed-seed replay; collision edge cases; stability and performance envelope. |
| **AI & NPC Systems** | Behavior trees, utility AI, pathfinding, tactical planning and opponent policies. | Engine navigation/AI; behavior-tree tools; Python experiment harness. | Scenario success, stuck-state detection, policy regression and bounded runtime. |
| **Networking & Multiplayer** | Replication, authority, matchmaking, lobby/session flow and server simulation. | ENet/WebSockets; Nakama/Colyseus when appropriate; Wireshark; network emulation. | Controlled test server; synchronization/reconnect tests; latency/loss evidence. |
| **UI/UX & Accessibility** | Menus, HUD, interaction, keyboard/controller/touch, localization and assistive paths. | Engine UI toolkit; Playwright for browser games; axe-core; screenshot/interaction harnesses. | Keyboard/controller navigation; contrast/text scaling; focus and accessibility regression. |
| **Tools & Content Pipeline** | Editors, importers, procedural tools, validators and asset build pipelines. | Blender Python; engine editor scripting; Python/Node CLI; JSON Schema. | Deterministic output; schema validation; idempotence; fixture-based tests. |
| **Platform & Performance** | Mobile lifecycle, device input, memory, CPU/GPU, thermal and frame pacing. | Android Studio Profiler; Perfetto; Tracy; RenderDoc; platform profilers. | Device/build matrix; p50/p95 frame time; memory/thermal budgets; resume/suspend tests. |
| **Build, Release & CI/CD** | Reproducible builds, packaging, signing integration, versioning and release automation. | Engine exporters; GitHub Actions; artifact manifests; SBOM/license tools. | Rebuild parity; artifact hash; clean install/launch; release checklist. |
| **ML, Vision & Telemetry** | Training/evaluation environments, screen/state perception, action control, replay analysis. | Unity ML-Agents; Gymnasium; Stable-Baselines3; PettingZoo; OpenCV; ONNX Runtime; Hugging Face datasets/Spaces. | Fixed benchmark tasks/seeds; train/eval separation; policy and telemetry receipts. |
| **Interoperability / Reverse Engineering** | Authorized format compatibility, protocol mapping, dependency/asset analysis and migration. | Ghidra; JADX; Apktool; Frida; mitmproxy; format-specific parsers. | Registered target, provenance, authorization, bounded capture, static/dynamic cross-validation. |

### Tool profile requirements

Every tool profile records:

- stable `tool_profile_id`, profile version and canonical upstream;
- supported specialist contexts, platform and engine versions;
- license/terms and whether commercial or hosted access is required;
- executable name/API/adapter and reproducible invocation;
- verified version or explicit `not_established` state;
- inputs, outputs, evidence types and artifact retention policy;
- CPU/GPU/RAM/storage/network expectations and remote-only constraints;
- sandboxing, target authorization, secrets-by-reference and cleanup/reset rules;
- maintainer, last verification, known limitations and reviewer.

**Catalog presence is not installation, account entitlement, live availability or proof of successful execution.** These states remain separate.

## 5. Autonomous work decomposition

The Game Development issue form is an intake/dispatch contract, not a provider selector. It feeds the existing queue and claim machinery only after QUE admission.

Default decomposition:

1. **Architect/producer** turns the brief into a GDD slice, requirement IDs, scene/system contracts and a dependency graph.
2. **Planner** separates independent work packages and assigns one accountable specialist to each package.
3. **Builders** implement independent assets/subsystems in parallel only when file ownership and interfaces do not overlap.
4. **Integrator** owns shared scenes, runtime wiring, package manifests and merge sequencing.
5. **Build verifier** runs static checks, engine import/build/export and deterministic tests.
6. **Playtest agent** executes approved scenarios against the built artifact and returns traces/replay/capture evidence.
7. **Independent QA/accessibility reviewer** reproduces outcomes without relying on the builder's self-report.
8. **Release reviewer** checks artifact provenance, license/attribution, platform requirements and rollback/recovery.

Initial fan-out is bounded to **three independent specialist packages** unless the issue explicitly justifies a larger dependency-safe wave and the manager approves it. Shared scene files, project manifests and engine configuration have one declared writer at a time.

### Work-package contract

Each package has: ID; accountable role; exact scope; dependencies; interface/contract; tool profiles; target/build identity; expected outputs; tests; resource budget; risk tier; reviewer; stop condition. Packages are linked back to the parent issue and context manifest.

The dispatch system must preserve the distinction between:
- requested specialists;
- specialists admitted by policy;
- candidates actually invoked;
- work packages completed;
- artifacts accepted after review.

No workflow may claim a parallel/nested topology unless the corresponding participants and hand-offs actually ran.

## 6. Verification ladder

Use the narrowest applicable checks first, but do not mistake a lower-level pass for a higher-level proof.

| Level | Verification | Example evidence |
|---|---|---|
| **V0 — Contract/static** | Schema, source, asset references, lint, type checks, dependency/license checks. | Validator output, source diff, asset manifest. |
| **V1 — Logic/unit** | Pure logic, state transitions, physics helpers, save/load, deterministic rules. | Unit test report, fixed-seed output. |
| **V2 — Engine/import/build** | Engine project import, resource compilation, shader compile, build/export. | Engine version, build log, artifact hash. |
| **V3 — Runtime interaction** | Launch actual build; scripted input; scene transitions; UI and gameplay actions. | Runtime log, trace, screenshots/video, interaction receipt. |
| **V4 — Scenario/playtest** | Objective completion, exploratory coverage, regression replay, accessibility paths. | Scenario report, replay reference, defect reproduction. |
| **V5 — Platform/performance** | Device/browser matrix, memory/frame-time/thermal/network budgets, lifecycle. | Profile capture, p50/p95 metrics, platform matrix. |
| **V6 — Release readiness** | Independent review, provenance/license, packaging, rollback, release checklist. | Reviewer verdict, signed/hashed artifact manifest, release receipt. |

A code-only review cannot certify visual fidelity, interaction behavior or a successful playthrough. Visual/runtime feedback is a required evidence leg for tasks that change visual or interactive behavior.

## 7. DoE specialist-pool evolution

DoE owns specialist population improvement. Game Development supplies stable task families, context manifests, tool profiles and outcome evidence; it does not independently promote or cull agents.

### Generational lifecycle

1. **Design:** register a campaign hypothesis, factors/levels, blocks, task suite, outcomes, decision rule, quota note and stop conditions before designed dispatch.
2. **Create cohort:** generate distinct candidate instances with stable IDs, parent lineage, prompt/tool hashes, role/context and generation number. A clone is a new candidate; it inherits no score, permission, reviewer status or target authorization.
3. **Assign treatments:** use the DoE-supported design generator (currently full factorial and Taguchi L9); randomized assignment is an assignment mechanism, not a design class.
4. **Execute:** one executed task/configured-instance run is one observation and emits one record conforming to `docs/ops/corpus/EXPERIMENT.schema.json`.
5. **Measure:** preserve execution status, task outcome, correctness, integration, regression, resource cost and reviewer verdict as distinct dimensions.
6. **Review:** compare against the pre-registered baseline and decision rule; distinguish provider/runtime failures from specialist performance.
7. **Select:** promote only a cohort that passes the declared gate. Cherry-pick successful prompt/tool/workflow slices into a **new version/generation**, retaining source lineage and comparison evidence.
8. **Cull/retire:** retain every experiment and lineage record; deactivation is reversible and never deletes the candidate's history. Protected QA, security and governance functions cannot be removed by autonomous score logic.
9. **Monitor:** compare generations on common task strata, detect regressions/saturation, and preserve the best-known checkpoint. A candidate that is merely registered or looks promising is not promoted.

### Measurement and attribution

- Key every configured instance by the DoE-required `treatment.instance` stamp: provider, model@version, exact system-prompt ref + SHA-256, tool manifest/canonical tool set ref + SHA-256, role, moniker, context and `instance_key`.
- Never pool different configured instances merely because they share a model name.
- A skipped, blocked or unexecuted treatment is not a successful run and is not a correctness failure.
- Keep game-player, game-QA, research and development scorecards separate.
- Selection fraction, sample size, confidence method and significance threshold must be pre-registered by DoE for the campaign; this lane invents no universal survivor percentage.
- The existing DoE standing significance gate applies where specified by the family; campaign-specific decision rules must be explicit before execution.

### Initial campaign proposal

`experiments/doe/game-development-specialist-evolution/DESIGN.json` is a **proposed design only**. It is not an admitted DoE campaign and contains no fabricated run records. DoE oversight must review and admit it, then create the first cohort and run evidence. The canonical family rule remains: a proposal alone is not a campaign member; committed design plus run evidence is required.

## 8. Issue-template and Reverse Engineering integration

- `.github/ISSUE_TEMPLATE/game-development-task.yml` is the new Game Development entry point. Its `issue-dispatch/v1` block routes through `swarm-admission`; the dedicated route waits for an admitted stamp before queueing the validated task.
- `project-task.py` remains the canonical required-field parser. The game form includes the exact `Entry`, `Task / spec`, `Scope`, and `Done-evidence` headings it expects.
- The existing **Target Brief** / Web Adapter Foundry route remains the Reverse Engineering and interoperability target-intake path. The separate APK Cross-Reference and Reverse Engineering Taxonomy forms remain their own research/tooling intake families. This change does not replace or silently rewire them.
- No untrusted issue text is executed as shell, code or instructions. Issue fields are data; tools resolve from reviewed profiles, never from free-form commands.

## 9. Safety, scope and stop conditions

Only project-owned, open-source, or explicitly authorized targets are eligible. Use controlled test accounts and project-controlled servers. No DRM/anti-cheat bypass, cracking, warez, unauthorized target probing, third-party exploitation or real-money wagering. Do not commit credentials, private captures, personal data or unlicensed assets.

Stop and request review when authorization is unclear, an artifact cannot be identified, the tool profile is unverified, a build changes external state, a work package exceeds its scope, a runner lacks required resources, or the verifier cannot reproduce the result.

## 10. Research basis and design implications

- **Game-Creation-Agents (2026):** a natural-language request is compiled into a multimodal design document, runtime scaffold, machine-readable contracts and deterministic tests; scenes are serialized, assets parallelized, then joined by a manifest; build-linked UI checks and a code-blind critic gate release. This supports dependency-aware work packages and an independent rendered-interface evaluator.
- **RSIGame (2026):** local explore → diagnose → improve loops are paired with a global quality/checkpoint loop that detects regression and saturation. This supports bounded repair, a best-known checkpoint and explicit stopping conditions.
- **A2Z GameSpec-Bench (2026):** long-form GDDs become dependency-aware contracts; source inspection is combined with scenario replay and adaptive playtesting. This supports requirement IDs and cross-system contract checks rather than prompt-only acceptance.
- **GameDevBench (ICML 2026):** 333 multimodal game-development tasks show agents struggle particularly with visual/asset-heavy work; image/video feedback improved measured performance. This supports visual evidence and specialist toolchains for graphics/animation, not only code review.
- **Unity ML-Agents:** game environments can be used for RL, imitation learning, neuroevolution, automated testing and design evaluation. This supports a distinct ML Game Research lane rather than folding player agents into development.
- **Automated game-testing research (2025):** online search agents can build and exploit models of game environments for navigation/exploration testing. This supports adaptive scenario exploration alongside fixed regression suites.

### Source links

- [Game-Creation-Agents (arXiv:2610.16776)](https://arxiv.org/abs/2610.16776)
- [RSIGame (arXiv:2609.39045)](https://arxiv.org/abs/2609.39045)
- [A2Z GameSpec-Bench (arXiv:2609.39564)](https://arxiv.org/abs/2609.39564)
- [GameDevBench, ICML 2026 / PMLR 306](https://proceedings.mlr.press/v306/chi26a.html)
- [Unity ML-Agents Toolkit](https://github.com/Unity-Technologies/ml-agents)
- [Unity AI Tools and CLI/MCP](https://unity.com/features/ai)
- [Godot command-line documentation](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html)
- [GdUnit4 CLI testing](https://godot-gdunit-labs.github.io/gdUnit4/latest/advanced_testing/cmd/)
- [Phaser 4 documentation](https://www.phaser.io/oss/docs)
- [Blender Python API automation](https://docs.blender.org/api/main/info_advanced_blender_as_bpy.html)
- [Automated Game Testing with Online Search Agent and Model Construction (2025)](https://doi.org/10.1002/stvr.70002)
