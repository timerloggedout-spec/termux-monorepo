# Game Player Fleet and Genre Teams

## Charter

The **Game Player Fleet** operationalizes the `Roster:Teams:Games:Players` label on [issue #243](https://github.com/timerloggedout-spec/termux-monorepo/issues/243#issue-5185983300). It is a first-class team lane, distinct from development and from game QA. Player machines play the project’s approved game list, generate structured session evidence, and provide genre-aware data to research, ML, QA, accessibility, and roster-calibration teams.

> **Operating separation:** Players play approved scenarios; developers build and repair the relevant systems; reviewers validate evidence and score events. A single candidate may contribute to more than one team only through separately recorded task cards and review outcomes.

The initial catalog named in issue #243 is Astro Loop, 2 Minutes in Space, UnCiv, Pixel StarShips, and an open-ended “MOAR!!” expansion path. New games, genres, players, machine types, and scorecards are appended through the registry model in [LABEL_TAXONOMY.md](./LABEL_TAXONOMY.md); no central role enum needs to be rewritten.

## Fleet Composition

| Team | Mission | Primary outputs | Independent review partner |
|---|---|---|---|
| Game Catalog & Intake | Maintain game identity, build provenance, genre tags, objectives, and assigned machine profiles. | Versioned game-catalog entries and target records. | Orchestration & Quality Control. |
| Player Machines | Run approved sessions, collect bounded telemetry, and recover to a reproducible baseline. | Session records, replay/trace references, reset evidence. | Game QA & Accessibility. |
| Genre Specialists | Design and execute genre-specific test scenarios and strategy/evaluation experiments. | Scenario suites, objective verdicts, balance observations. | Research & Intelligence. |
| Game QA & Accessibility | Independently reproduce player findings and assess user-facing quality. | Defect reports, accessibility observations, verified regressions. | Development. |
| ML Game Research | Evaluate and compare permitted model, vision, planning, or control stacks against the catalog. | Benchmark reports, feature/telemetry recommendations, experiment cards. | Research & Intelligence. |
| Fleet Reliability | Maintain images, emulator/device configuration, telemetry collectors, and reset procedures. | Machine profiles, health records, resource reports, recovery runbooks. | Delivery Reliability / CI-CD. |

## Genre Role Families

A player role is not a generic “game player” score. Every role has a declared genre, scenario class, machine profile, and scorecard. Initial role families are deliberately broad so specialized roles can be appended when the catalog grows.

| Role family | Suitable scenario classes | Measures that matter |
|---|---|---|
| Strategy / 4X player | Long-horizon decision trees, match flow, resource management, balance and AI behavior. | Objective completion, decision-trace coverage, session stability, resource efficiency. |
| Action / arcade player | Input-sensitive controls, performance-intensive scenes, progression, recoverable failure states. | Input fidelity, frame-time stability, scenario coverage, reproducible failure traces. |
| Simulation / builder player | Economy loops, construction, saving/loading, UI interactions, long-running states. | State integrity, save/load reliability, scenario completion, accessibility observations. |
| Puzzle / educational player | Progression logic, hints, localization, learning paths, accessibility alternatives. | Path coverage, completion consistency, usability evidence, defect reproduction quality. |
| Multiplayer test player | Project-controlled test servers, test accounts, controlled match configurations. | Session setup reliability, network trace quality, synchronization observations, reset correctness. |
| Accessibility reviewer | Assistive interactions, visual/text alternatives, input flexibility, localization and readability. | Issue impact clarity, repeatability, verification quality, regression prevention. |

## Machine Profile Contract

Every game-playing machine is a managed capability, not an anonymous host. A machine profile must be sufficient to reproduce a session, understand its limits, and reset it after an experiment.

| Field | Requirement |
|---|---|
| `machine_id` | Stable, non-secret identifier such as `android-emulator-a14-01` or `desktop-vm-linux-01`. |
| `profile_version` | Version of the operating system, image, game runtime, and capture stack. |
| `hardware_class` | Device/emulator/VM type, CPU/GPU/RAM class, display configuration, and input capability. |
| `game_manifest` | Explicit catalog entries and build hashes that may run on the machine. |
| `test_profile` | Approved test-account or local-profile identifier; never store credentials in Git. |
| `input_mode` | Touch, keyboard, controller, accessibility interface, scripted regression harness, or other declared mode. |
| `telemetry_policy` | Allowed event types, retention location, redaction requirements, and session identifier format. |
| `resource_limits` | Time, storage, network, battery/thermal, and parallel-session constraints. |
| `reset_procedure` | Steps and evidence that return the machine to its known baseline. |
| `owner_team` | Fleet Reliability owner and review partner. |

## Game Catalog Contract

| Field | Requirement |
|---|---|
| `game_id` | Stable roster identifier independent of display name. |
| `title` and `genre_tags` | Human-readable name and one or more genre markers. |
| `approval_source` | Project ownership, open-source provenance, or explicit contributor authorization. |
| `build_identity` | Version, artifact hash when available, source URL, and platform. |
| `objectives` | Approved research, QA, accessibility, or benchmark scenarios. |
| `machine_profiles` | Compatible and assigned player-machine profiles. |
| `team_assignments` | Primary genre players, QA reviewer, ML researcher, and development counterpart. |
| `evidence_policy` | Required session traces, performance logs, screenshots, replay references, and report format. |
| `reset_and_escalation` | Failure recovery path and owner for suspected platform, build, or environment faults. |

## Score Events

The Game Player Fleet writes score events only after the task card, game catalog entry, machine profile, session evidence, and review disposition are complete. Raw time played, cosmetic rank, or a score from another genre is not enough to demonstrate role fitness.

| Score event | Evidence minimum | Example use |
|---|---|---|
| `scenario_completed` | Scenario ID, build ID, machine ID, session trace, objective verdict. | Verify a strategy player can execute a prescribed long-horizon scenario. |
| `session_stable` | Runtime duration, crash/error record, resource profile, reset verification. | Establish a machine profile’s reliability for a given game. |
| `reproducible_game_finding` | Steps, expected/actual behavior, affected build, reviewer reproduction. | Award QA evidence for a verified defect. |
| `accessibility_path_verified` | Assistive input/display configuration, task path, observed limitation or success. | Evaluate an accessibility reviewer role. |
| `telemetry_complete` | Required fields present, no prohibited data, trace retained at approved location. | Evaluate fleet-operation discipline. |
| `experiment_invalidated` | Reason: environment fault, broken build, missing data, or incorrect task specification. | Prevent inaccurate performance penalties. |

## Initial Delivery Sequence

The first implementation increment is documentation and schema only: add a game catalog, machine-profile schema, player task card, and score-event examples. The second increment provisions a single controlled Android emulator or disposable desktop VM profile for one approved build. The third increment adds a second genre and independent reviewer to test the additivity of the model before creating a wider fleet.

No fleet expansion should be counted as complete until the catalog entry, machine profile, telemetry policy, reset record, and reviewer pairing are all present. This gives the “Players Play && Devs Dev” directive a reproducible operating form while leaving room for new game lists, genres, machines, and teams.

## References

[1] [Issue #243 — Game Teams](https://github.com/timerloggedout-spec/termux-monorepo/issues/243#issue-5185983300)

[2] [Label Recon and Additive Team Taxonomy](./LABEL_TAXONOMY.md)

[3] [Issue #236 — .APK Investigation List](https://github.com/timerloggedout-spec/termux-monorepo/issues/236)
