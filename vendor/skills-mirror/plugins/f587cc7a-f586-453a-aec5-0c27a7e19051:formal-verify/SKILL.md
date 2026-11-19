---
name: formal-verify
description: "Model-check thread protocols with TLA+ and TLC, prove sequential invariants with Lean 4, and check bounded Rust functions with Kani. Map counter-examples to source locations, reproductions and fixes, and keep the models in CI. Use for /agent-formal-verify:formal-verify, formal verification, model checking, Lean proofs, Kani, bounded Rust verification, or concurrency bugs that runtime tests cannot reproduce."
---

# Formal verify

Model individual protocols or sequential invariants. Map counter-examples to events and locations in the source code. Before reporting a pass, confirm that each checked property detects a relevant mutation and that its checker passes.

Choose tools according to the target:

| What can go wrong | Tool | Why |
| --- | --- | --- |
| Thread interleavings that lose wakeups, free resources twice, deliver items twice or out of order, block close, or report errors on the wrong thread | TLA+ with TLC | TLC explores the states of a small instance and reports counter-examples |
| Overflow, out-of-bounds access, panics and broken invariants in a Rust function with bounded loops | Kani | Kani checks the real code for every input within the stated bounds |
| Arithmetic or sequential transitions that break bounds, invariants or encoder round trips, or reach states the code assumes impossible | Lean 4 | Evaluate bounded instances, then prove the property for every size |

Prefer Kani when the function is Rust and its inputs and loops can be bounded, because it checks the production function directly. Use Lean when the property must hold for every size or the code is not Rust.

A thread protocol that depends on arithmetic such as `slot = item mod window` needs both tools. Use TLA+ for the interleavings with the arithmetic as a constant, and Lean for the arithmetic.

## 1. Pick the targets

Search with `rg` for `pthread_cond`, `pthread_mutex`, `atomic_`, `std::condition_variable`, `sync.Cond`, `chan`, `select`, `asyncio.Condition`, `Semaphore`, `atexit` and `setjmp`. Also search for protocol state names such as `ready`, `stop`, `done`, `finished`, `pending`, `inflight`, `head`, `tail` and `exiting`. Classify each hit:

- Model hand-written protocols, including hand-overs, bounded pipelines, queues with ordered output, shutdown, cleanup, retry and lease loops.
- Leave data-parallel loops over disjoint indices to ThreadSanitizer or the language's race detector, and say so in the reply.
- For library-owned channels or executors, model the calling code.
- Use Lean for arithmetic the protocol or output depends on. Examples include slot and splice indices, window bounds, sizes computed and checked differently, and encoder round trips. Search for `%`, `- 1`, `+ 1`, `>>`, `overlap`, `splice` and `offset` near the protocol's data.

For Rust functions, also search for `unsafe`, `as u32`, `as usize`, `checked_`, `wrapping_`, `unwrap(`, slicing and `%`. Record each function's input ranges, loop bounds and assumptions for a Kani target.

Write a table with one row per target before modelling. A protocol and the arithmetic it depends on are separate targets. For a protocol, record its threads, shared variables, every wait and what wakes it, terminal states such as joined or closed, and resources whose ownership moves. Include slots, buffers, file handles and resources that `close` frees. For a Lean target, record the functions, their integer types and the property. Start with waits that have no escape, resources freed by two paths, and errors raised on a different thread from the one that reports them. Read the whole source file for each target so the model follows the code.

## 2. Prepare the tools

Prepare tools after picking targets and before launching agents. The helpers are in this skill's `scripts/` directory. Stay in the target repository and run each helper with `bash` and its absolute path. Pass absolute paths to models and matrices. [Tool setup](references/setup.md) describes the pins, caches and environment settings.

- When a target needs Kani, run `bash <skill-dir>/scripts/setup.sh rust`. Copy the Kani template into a verification crate only when it helps add harnesses that call the production function.
- When a target needs TLA+, run `bash <skill-dir>/scripts/setup.sh tla`.
- When a target needs Lean, every Lean model in the repository shares one Lake project. If the repository has none, copy `lakefile.toml`, `lake-manifest.json` and `lean-toolchain` from `<skill-dir>/examples/lean-template/` to `lean/` in the target repository, once. Then run `bash <skill-dir>/scripts/setup.sh lean <absolute-model-project-path>`.

Require a successful exit and a `READY` line from each command. A helper that cannot run prints `UNAVAILABLE` and exits 3. Report it as "not checked" with its remedy. It is neither a pass nor a failure of the model. A check that ran and failed exits 1; usage errors exit 2. The setup helper reuses ready tools and installs a missing Lean pin, so the user does not need to rerun `/agent-formal-verify:setup` when a target or pin changes. Keep the installed skill files read-only and copy templates into the target repository.

If a system prerequisite such as Java or elan is missing, use the [setup skill](../setup/SKILL.md) to prepare it within the user's installation constraints and existing authorization. Report any prerequisite that cannot be prepared. If `java` on PATH has no runtime, set `JAVA` to a working JDK's `java` binary for the setup helper and the matrix runner.

The helpers:

- The setup helper, [`scripts/setup.sh`](scripts/setup.sh), verifies the pinned TLC JAR and is the only helper that installs a Lean toolchain.
- The matrix runner, [`scripts/tlc-matrix.sh`](scripts/tlc-matrix.sh), runs TLC with a matrix of constants and prints one PASS or FAIL per run with its state count, then a SUMMARY line with the totals. A failing run prints its error trace reduced by [`scripts/tlc-trace.py`](scripts/tlc-trace.py) to the variables each step changed. Copy [`examples/tla-template/`](examples/tla-template/BoundedQueue.tla) to start a spec and its matrix.
- The Lean checker, [`scripts/lean-check.sh`](scripts/lean-check.sh), builds every `.lean` file in the pinned Lake project and audits every declaration of every built module. It fails on a build error, a `sorry`, a declaration that rests on an axiom beyond `propext`, `Classical.choice` and `Quot.sound`, or a `.lean` file that no Lake library owns. Use `--freeze` before the file names to record statement types and definition bodies in each model's `.statements` file before proving it. Freezing permits `sorry` and reports FROZEN, not a proof PASS. Later checks enforce those records and permit proof changes and added declarations. Given file names after the project, it checks only those files. Copy [`examples/lean-template/Model/BoundedQueue.lean`](examples/lean-template/Model/BoundedQueue.lean) to start a model.
- The Rust checker, [`scripts/kani-check.sh`](scripts/kani-check.sh), runs the pinned Kani on the crate's proof harnesses. It reports each harness's unwind bound and check count, rejects failed checks and unsatisfied cover conditions, and prints concrete playback tests when available. Copy [`examples/kani-template/`](examples/kani-template/src/lib.rs) for a bounded-queue example.
- The mutation runner, [`scripts/mutate.py`](scripts/mutate.py), takes a model's `<Name>.mutations` file and applies each listed bug to a temporary copy of the model. It prints DETECTED or MISSED per mutation with what failed, UNCOVERED for a TLA+ property or Kani harness that no mutation targets, and a SUMMARY line. All three templates include a mutations file.

## 3. Model one target per agent

Spawn one agent per target, in parallel when supported. Use the host runtime's agent tools and follow the user's model configuration when selecting agents. An agent does not see this skill. Its brief contains:

- the target's row from the table, with its source files and line ranges;
- the model's name, `<Name>`, and for a Lean target the absolute path of the Lake project, or for Kani the absolute path of the crate;
- the absolute path of this skill's directory as `<skill-dir>`, and any `JAVA` setting;
- the instruction to read `<skill-dir>/references/tla-brief.md` for a protocol, `<skill-dir>/references/lean-brief.md` for arithmetic, or `<skill-dir>/references/rust-brief.md` for a Rust function, in full and to follow it.

Name the brief file and leave its text out of the prompt. The [TLA+ brief](references/tla-brief.md), the [Lean brief](references/lean-brief.md) and the [Rust brief](references/rust-brief.md) hold the modelling requirements, the files to write, the commands to run and what to report. If delegation is unavailable, read the brief for each target and model the targets yourself, one at a time.

An agent writes only its own files, `tla/<Name>.tla`, `.matrix` and `.mutations`, `lean/Model/<Name>.lean`, `.mutations` and `.statements`, or the assigned Rust harness and `.mutations` files in a separate crate, so parallel agents share none. When Rust agents have reported, run the Rust checker on each crate. When the Lean agents have reported, run the Lean checker on the whole project, without a file name. An existing Lean project keeps its layout and must pin Lean 4.20.0 or later.

## 4. Read the counter-example back into the code

For a closed Lean proof, compare the model's printed differential vectors with the production function in the repository's native test framework. Report the agreement count and integer widths. Claim that the proof describes the code only after this comparison agrees, or state beside the verdict that the vectors were not run.

For each violation, in this order:

1. Read the reduced trace that the matrix runner prints under the FAIL line, the inputs that Lean's bounded search prints, or Kani's failed check and playback inputs. Map each step to a code event and source line.
2. Check reachability against the real constants and callers. If a violation occurs at `Slots=1` while the code ships `Slots=4`, decide whether the trace needs the smaller count or can also occur at the shipped one. Report the first as safe only while the count stays at the shipped value, and the second as a reachable bug. Keep the boundary configuration in the matrix either way.
3. Reproduce a reachable trace with a deterministic test, a ThreadSanitizer or race-detector run, or a stress loop using the trace's counts. Hooks, a small slot count or barriers can force the interleaving. If no practical reproduction exists, report that limitation and the model configuration that demonstrates the violation.
4. Change code only when the user asked for fixes. Otherwise report the trace, the reproduction and the proposed fix, and stop here. The model then describes the code as written, so its failing check is the record of the bug. Do not reword the property to pass, prove its negation or add runs that expect failure. Mutations for a failing property wait for the fix.
5. Apply the smallest fix that prevents the trace, update the model to match, and rerun its matrix, the Lean checker or the Rust checker, then its mutations. Keep the model and code change together.
6. When the user asked for commits or pull requests, use one PR per bug. Include the model, its mutations file and the fix. Write the description as the Reply section says.

## 5. Keep the proof, and record each result once

Add CI only when the user asked for it or the repository already runs models in CI. Otherwise give the commands in the reply. The CI section of [tool setup](references/setup.md) describes how a CI job obtains the helpers, which are not in the target repository, and prepares the tools in a separate setup step. CI runs the matrix runner on each matrix file, the Lean checker on the project, the Rust checker on each crate and the mutation runner on each mutations file.

Each fact about a model has one home:

- The model's header comment names the source files and line ranges it follows and its assumptions. Refresh them when the code moves.
- The mutations file lists the bugs the model detects.
- The project's testing documentation, when it has any, has one row per model: what it checks, in the words the Reply section asks for, and its boundary configuration.
- A pull request description tells its bug's story once and links to the model.

Do not add a report file per bug, and do not paste run tables or traces into several documents. Write `<skill-dir>` for the installed skill in any committed command; a path from this machine does not work for the next reader.

## What this does not cover

These models do not check memory ordering below the mutex. Keep the project's ThreadSanitizer or race-detector checks. Model floating-point results as the integers they round to, unless the property concerns the rounding itself.

A passing TLA+ or Lean model establishes its stated properties under its assumptions. It describes the code by hand. Kani checks the Rust function itself, within the reported input and unwind bounds. Neither result establishes correctness of the whole program.

## Reply

Write the reply, and any pull request or document, for a reader who knows the code and has used none of these tools.

1. Start with what was found, in the code's terms. For each bug, say what goes wrong for a caller or user, the code events in order with `file:line`, whether the shipped settings can reach it, how to reproduce it, and the fix or proposed fix, with a PR link when one was opened.
2. Give a table with one row per target: what was checked, as a sentence about the code, and the verdict. Label each counter-example `reproduced`, `reachable at shipped settings`, or `model-only`. State each property as what it guarantees, such as "the bar never shows 100% before the work finishes". Add the model's name for it in backticks only so the reader can find it.
3. Say what each kind of evidence means where it first appears:

   | Evidence | Meaning to give |
   | --- | --- |
   | TLC passes | TLC tried every ordering of the modelled steps at the listed small sizes and found none that breaks the property. The SUMMARY line's state total is the size of that search, not a count of real runs. |
   | Kani passes | Kani checked every input within the stated bounds and found no violation. Larger inputs are not covered. |
   | Lean passes | Lean proved the property for every input, under the listed assumptions. |
   | A bounded search passes | Every input up to the stated bound was tried. |
   | Mutations detected | Deliberate bugs were planted in copies of the model, and the checks caught each one. This shows the checks can fail. |
   | UNAVAILABLE | The tool could not run. This target was not checked; give the printed remedy. |
   | reproduced | A deterministic test or race-detector run fails on the production code. |
   | reachable at shipped settings | The shipped constants and callers permit the counter-example, but no production reproduction has confirmed it yet. |
   | model-only | The counter-example needs a configuration or caller the shipped code does not use. |
   | Counter-example | A step-by-step schedule or an input that breaks the property. |

4. Give a term of any tool its meaning beside it: an invariant is always true, a liveness property says something eventually happens, fairness assumes a thread that can run does run, an axiom is taken without proof, and `sorry` marks an unfinished proof.
5. Say what a pass leaves open: the sizes TLC checked, the code constraints the model omits, each theorem's hypotheses and integer widths, and the properties that could not be expressed.
6. End with the commands to recheck and their SUMMARY and PASS lines.
