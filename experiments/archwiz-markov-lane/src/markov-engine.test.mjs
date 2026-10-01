import assert from "node:assert/strict";
import {
  assertClose,
  compareGrowth,
  layerProbability,
  recombiningTrellis,
  samplePath,
  strictTree,
  validateChain
} from "./markov-engine.mjs";

const states = ["Idle", "Scan", "Process", "Sync"];
const transitions = {
  Idle: { Scan: 0.7, Process: 0.3 },
  Scan: { Scan: 0.2, Process: 0.6, Sync: 0.2 },
  Process: { Process: 0.4, Sync: 0.6 },
  Sync: { Sync: 1 }
};
const initial = { Idle: 1, Scan: 0, Process: 0, Sync: 0 };

assert.equal(validateChain(states, transitions), true);

const tree = strictTree({ states, transitions, initial, horizon: 4 });
const trellis = recombiningTrellis({ states, transitions, initial, horizon: 4 });

for (const { total } of layerProbability(trellis)) assertClose(total, 1);
for (const { total } of layerProbability(tree)) assertClose(total, 1);

const growth = compareGrowth(tree, trellis);
assert.ok(growth[4].treeNodes > growth[4].trellisNodes);
assert.equal(trellis[4].nodes.length, states.length);

const sync = trellis[4].nodes.find((node) => node.state === "Sync");
assert.ok(sync.probability > 0);
assert.ok(sync.incoming.length > 0);

const sampled = samplePath({
  start: "Idle",
  transitions,
  steps: 5,
  random: () => 0.5
});
assert.equal(sampled[0], "Idle");
assert.equal(sampled.length, 6);

assert.throws(() => validateChain(["A"], { A: { A: 0.8 } }), /expected 1/);

console.log("PASS markov-engine deterministic fixtures");
console.table(growth);
