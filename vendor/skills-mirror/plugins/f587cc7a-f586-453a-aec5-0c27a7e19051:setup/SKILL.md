---
name: setup
description: "Prepare all shared tools for the agent-formal-verify plugin: Java, Python, TLC, elan, Lean, Rust and Kani. Use for initial installation, missing prerequisites, or /agent-formal-verify:setup."
---

# Set up formal verification tools

Prepare the complete shared toolset once, independently of any repository. Verification selects TLA+, Lean and Kani from each repository's current targets. A global plugin installation uses the same tools across repositories.

1. Read [tool setup](../formal-verify/references/setup.md) for pinned versions and environment settings. Inspect the operating system and existing runtimes. Reuse installed prerequisites and tool caches.
2. Ensure a working JDK, Python 3, a SHA256 tool, elan, Rust, the pinned Kani and the pinned TLC JAR are available. Install missing prerequisites through the user's existing package manager or the upstream documented installer, following their installation constraints. Obtain `tla2tools.jar` from the TLA+ release that `scripts/tlc-tools.sh` pins and save it at the path the helper names; the helper verifies its SHA256 and downloads nothing itself. If no suitable installation method is available, or the user has not allowed installation, report the missing prerequisites and their installation instructions.

   Install the Kani version from tool setup with Cargo, then run `cargo kani setup`. The plugin's helpers verify it without installing or downloading it.

3. Check that `java -version` succeeds. If `java` is not on PATH or macOS resolves it to a stub, set `JAVA` to the working JDK's `java` binary for the commands below, and report that setting, because verification needs it too.
4. Run the three commands below with the absolute path of the `formal-verify` skill, which is this skill's sibling directory, in place of `<skill-dir>`. Treat installed plugin files as read-only. The Lean template supplies the default pin without creating a model project or changing elan's global default.

   ```shell
   bash <skill-dir>/scripts/setup.sh rust
   bash <skill-dir>/scripts/setup.sh tla
   bash <skill-dir>/scripts/setup.sh lean <skill-dir>/examples/lean-template
   ```

5. Require a successful exit and a `READY` line from all three commands. Report the tool versions or pins, any environment settings required for verification, and anything still missing. Readiness confirms the tooling; the matrix runner and Lean checker check model correctness. Repeating setup reuses prepared tools. Verification handles repository-specific Lean pins when needed.
