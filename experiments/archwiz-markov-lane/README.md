# ArchWiz Markov Trellis Sandbox

This directory is intentionally isolated from production routing and the context-relationship graph.

## Files

- index.html — interactive canvas sandbox.
- src/markov-engine.mjs — deterministic Markov/tree/trellis model.
- src/markov-engine.test.mjs — Node-native invariant tests.
- src/archwiz-markov-trellis.jsx — React/SVG reference implementation for later UI integration.

## Versioned Tribute surface

- `VERSION.json` records the experiment-lane version (`0.1.0`).
- The interactive surface is published through Tribute at `apps/tribute-dashboard/markov-trellis.html`.
- The nested version header links back to this source lane, model, tests, and version record.
- The shared dashboard build manifest hashes the published `markov-engine.mjs` runtime asset.

## Model contract

The transition matrix is the source of truth. The UI consumes computed node probabilities and provenance; it does not invent weights.

Strict tree:
- each transition creates a new path occurrence.

Recombining trellis:
- equivalent (time,state) occurrences merge;
- node probability is the sum of all incoming path probabilities;
- incoming edges retain their individual contribution.

Monte-Carlo particles:
- sampled from the same transition matrix;
- deterministic tests inject a seeded/random callback.

## Run

    python3 -m http.server 4173 --directory experiments/archwiz-markov-lane

Then open http://localhost:4173/.

    node experiments/archwiz-markov-lane/src/markov-engine.test.mjs
