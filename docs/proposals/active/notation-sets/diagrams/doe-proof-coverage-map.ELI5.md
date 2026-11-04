# ELI5 — doe-proof-coverage-map.mmd

**What the diagram shows:** every experiment in the program,
sorted by how much of its proof exists. Proofs here are
machine-checked: a computer program verifies the math, so the
claim does not rest on anyone's say-so.

**What it means, in plain words:**

- The top group (3 items) has *part* of its proof written. The
  machine check on that batch **FAILED** — and the failure is
  printed on the picture, not hidden. One of the three (the
  "snapshot method") is marked in red because its proof is not
  just unfinished — as written, it is broken. Fixing it means a
  corrected attempt and a fresh machine check, not a quiet edit.
- The middle group (1 item) has its claims written down in
  formal language but no proof yet. Its scoring happens at a
  fixed future date, and the proof rides that.
- The big group (22 items) has no formal proof yet. That does
  NOT mean those experiments have no evidence — several are
  backed by tests and double-checked counts. It means one
  specific extra check (the machine-checked proof) is still
  owed, so in the register they read "incomplete."

**What the diagram does NOT show:** what each open item still
owes, or the evidence those items do have. And it never upgrades
a result: a failed check stays failed on this picture until a
new, passing check replaces it in the record.
