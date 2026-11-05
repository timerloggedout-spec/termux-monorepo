const SUPPORTED_PLANES = new Set([
  'github', 'x', 'research-seeds', 'papers', 'following', 'challenge',
]);

function isRecord(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function nonEmptyString(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

function validateEdge(value, where) {
  if (!isRecord(value)) throw new Error(`${where} must be an object.`);
  if (!nonEmptyString(value.src)) throw new Error(`${where} needs a non-empty src string.`);
  if (!nonEmptyString(value.dst)) throw new Error(`${where} needs a non-empty dst string.`);
  if (!nonEmptyString(value.type)) throw new Error(`${where} needs a non-empty type string.`);
  const evidence = value.evidence;
  if (!isRecord(evidence)) throw new Error(`${where} needs an evidence object.`);
  if (!SUPPORTED_PLANES.has(evidence.plane)) {
    throw new Error(`${where} has an unsupported evidence plane.`);
  }
  if (!nonEmptyString(evidence.record)) throw new Error(`${where} evidence.record must be a non-empty string.`);
  if (!nonEmptyString(evidence.method)) throw new Error(`${where} evidence.method must be a non-empty string.`);
  if (!Object.prototype.hasOwnProperty.call(evidence, 'observed_at')) {
    throw new Error(`${where} evidence.observed_at is required (use null when unavailable).`);
  }
  if (evidence.observed_at !== null &&
      (!nonEmptyString(evidence.observed_at) || !Number.isFinite(Date.parse(evidence.observed_at)))) {
    throw new Error(`${where} evidence.observed_at must be a valid timestamp string or null.`);
  }
  return value;
}

function normalizeNode(value, where) {
  if (!isRecord(value) || !nonEmptyString(value.id) || !nonEmptyString(value.label)) {
    throw new Error(`${where} needs string id and label fields.`);
  }
  const inferred = value.id.split(':');
  const plane = value.plane ?? inferred[0];
  if (!SUPPORTED_PLANES.has(plane)) {
    throw new Error(`${where} has an unsupported plane.`);
  }
  if (value.parentId !== undefined && !nonEmptyString(value.parentId)) {
    throw new Error(`${where} parentId must be a non-empty string when supplied.`);
  }
  if (value.attributes !== undefined && !isRecord(value.attributes)) {
    throw new Error(`${where} attributes must be an object of string values.`);
  }
  const attributes = value.attributes ?? {};
  for (const [key, item] of Object.entries(attributes)) {
    if (!nonEmptyString(key) || typeof item !== 'string') {
      throw new Error(`${where} attributes must contain string values.`);
    }
  }
  return {
    ...value,
    id: value.id,
    label: value.label,
    kind: nonEmptyString(value.kind) ? value.kind : inferred[1] || 'entity',
    plane,
    description: typeof value.description === 'string' ? value.description : 'Imported entity.',
    attributes,
  };
}

export function parseGraphImport(raw, fileName) {
  const name = String(fileName || 'import').toLowerCase();
  const isLines = name.endsWith('.jsonl') || name.endsWith('.ndjson');
  let nodes = [];
  let edges = [];

  if (isLines) {
    for (const [index, line] of String(raw).split(/\r?\n/).entries()) {
      if (!line.trim()) continue;
      let item;
      try {
        item = JSON.parse(line);
      } catch {
        throw new Error(`Invalid JSON on line ${index + 1} of ${fileName}.`);
      }
      edges.push(validateEdge(item, `Line ${index + 1} of ${fileName}`));
    }
  } else if (name.endsWith('.json')) {
    let payload;
    try {
      payload = JSON.parse(String(raw));
    } catch {
      throw new Error(`Invalid JSON in ${fileName}.`);
    }
    if (Array.isArray(payload)) {
      edges = payload.map((edge, index) => validateEdge(edge, `Edge ${index + 1} of ${fileName}`));
    } else if (isRecord(payload)) {
      if (payload.nodes !== undefined && !Array.isArray(payload.nodes)) {
        throw new Error(`nodes in ${fileName} must be an array.`);
      }
      if (payload.edges !== undefined && !Array.isArray(payload.edges)) {
        throw new Error(`edges in ${fileName} must be an array.`);
      }
      nodes = (payload.nodes || []).map((node, index) => normalizeNode(node, `Node ${index + 1} of ${fileName}`));
      edges = (payload.edges || []).map((edge, index) => validateEdge(edge, `Edge ${index + 1} of ${fileName}`));
    } else {
      throw new Error(`${fileName} must contain a JSON object or edge array.`);
    }
  } else {
    throw new Error(`Unsupported file: ${fileName}. Use JSON or JSONL.`);
  }

  return { nodes, edges };
}
