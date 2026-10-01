export const EPSILON = 1e-9;

export function assertClose(actual, expected, epsilon = EPSILON) {
  if (Math.abs(actual - expected) > epsilon) {
    throw new Error(`expected ${expected}, got ${actual}`);
  }
}

export function validateChain(states, transitions) {
  if (!Array.isArray(states) || states.length === 0) throw new Error("states must be non-empty");
  const stateSet = new Set(states);
  for (const state of states) {
    const row = transitions[state];
    if (!row) throw new Error(`missing transition row: ${state}`);
    let sum = 0;
    for (const [target, weight] of Object.entries(row)) {
      if (!stateSet.has(target)) throw new Error(`unknown target state: ${target}`);
      if (!Number.isFinite(weight) || weight < 0) throw new Error(`invalid transition weight: ${state}->${target}`);
      sum += weight;
    }
    assertClose(sum, 1);
  }
  return true;
}

export function normalizeDistribution(states, distribution) {
  const result = {};
  let total = 0;
  for (const state of states) {
    const value = Number(distribution[state] ?? 0);
    if (!Number.isFinite(value) || value < 0) throw new Error(`invalid distribution weight: ${state}`);
    result[state] = value;
    total += value;
  }
  assertClose(total, 1);
  return result;
}

export function propagate(states, transitions, distribution) {
  const next = Object.fromEntries(states.map((state) => [state, 0]));
  for (const from of states) {
    for (const [to, weight] of Object.entries(transitions[from])) {
      next[to] += distribution[from] * weight;
    }
  }
  return next;
}

export function recombiningTrellis({ states, transitions, initial, horizon = 3 }) {
  validateChain(states, transitions);
  let distribution = normalizeDistribution(states, initial);
  const layers = [{ time: 0, nodes: states.map((state) => ({
    id: `t0:${state}`, time: 0, state, probability: distribution[state],
    incoming: [], provenance: distribution[state] > 0 ? [{ path: [state], probability: distribution[state] }] : []
  })) }];

  for (let time = 1; time <= horizon; time += 1) {
    const incoming = Object.fromEntries(states.map((state) => [state, []]));
    const next = Object.fromEntries(states.map((state) => [state, 0]));

    for (const fromNode of layers[time - 1].nodes) {
      if (fromNode.probability === 0) continue;
      for (const [to, weight] of Object.entries(transitions[fromNode.state])) {
        const pathProbability = fromNode.probability * weight;
        next[to] += pathProbability;
        incoming[to].push({
          from: fromNode.id,
          probability: pathProbability,
          transition: weight
        });
      }
    }

    layers.push({
      time,
      nodes: states.map((state) => ({
        id: `t${time}:${state}`,
        time,
        state,
        probability: next[state],
        incoming: incoming[state],
        provenance: []
      }))
    });
    distribution = next;
  }

  return layers;
}

export function strictTree({ states, transitions, initial, horizon = 3 }) {
  validateChain(states, transitions);
  const start = normalizeDistribution(states, initial);
  let leaves = states
    .filter((state) => start[state] > 0)
    .map((state, index) => ({
      id: `t0:n${index}`, time: 0, state, probability: start[state],
      path: [state], parent: null
    }));
  const layers = [{ time: 0, nodes: leaves }];

  for (let time = 1; time <= horizon; time += 1) {
    const next = [];
    for (const parent of leaves) {
      for (const [to, weight] of Object.entries(transitions[parent.state])) {
        const path = [...parent.path, to];
        next.push({
          id: `t${time}:${path.join(">")}`,
          time,
          state: to,
          probability: parent.probability * weight,
          path,
          parent: parent.id,
          transition: weight
        });
      }
    }
    leaves = next;
    layers.push({ time, nodes: leaves });
  }
  return layers;
}

export function layerProbability(layers) {
  return layers.map((layer) => ({
    time: layer.time,
    total: layer.nodes.reduce((sum, node) => sum + node.probability, 0)
  }));
}

export function compareGrowth(treeLayers, trellisLayers) {
  return treeLayers.map((layer, index) => ({
    time: layer.time,
    treeNodes: layer.nodes.length,
    trellisNodes: trellisLayers[index]?.nodes.length ?? 0
  }));
}

export function sampleNext(state, transitions, random = Math.random) {
  const draw = random();
  if (!(draw >= 0 && draw < 1)) throw new Error("random source must return [0,1)");
  let cumulative = 0;
  for (const [target, weight] of Object.entries(transitions[state])) {
    cumulative += weight;
    if (draw < cumulative) return target;
  }
  return Object.keys(transitions[state]).at(-1);
}

export function samplePath({ start, transitions, steps, random = Math.random }) {
  const path = [start];
  let state = start;
  for (let i = 0; i < steps; i += 1) {
    state = sampleNext(state, transitions, random);
    path.push(state);
  }
  return path;
}
