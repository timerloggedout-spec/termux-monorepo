# ELI5 — e001-cycle-state.mmd

**What the diagram shows:** the eight steps of one experiment
cycle, drawn as boxes, with arrows for every move the rules allow.
If there is no arrow between two steps, that move is not allowed.

**What it means, in plain words:**

- Every cycle starts by writing down what will be tested, before
  anything is built ("preregister"). No skipping this.
- Then: build it, check it, get a second independent check, decide
  the verdict, and write the result into the record.
- After recording, there are two ways forward: add a new layer —
  which sends the cycle back to "check it" again — or close the
  cycle out.
- "Close" is final. Nothing leaves the closed state.

**What the diagram does NOT show:** *when* a move is allowed, only
*that* it is allowed. For example, going back to "check it" is
meant to happen only when something materially changed, and the
second check must really be a second check, not the same one
repeated. Those conditions are written in the method's text, not
in this picture. The picture gives you the map; the text gives
you the traffic rules.
