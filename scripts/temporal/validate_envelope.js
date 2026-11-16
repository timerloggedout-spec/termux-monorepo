#!/usr/bin/env node
// Evidence-envelope validator — JAVASCRIPT generation (V4 contract-first).
// Mirror of validate_envelope.py for envelope_schema.json
// (evidence-envelope/v1): returns the AGGREGATED violation list.
// Usage: node validate_envelope.js <payload.json>  -> prints violations JSON.
"use strict";
const fs = require("fs");
const REQUIRED = ["workflow_id", "unit_id", "receipt_sha256", "receipt_count",
                  "history_sha256", "unknown_outcomes"];
const SHA256 = /^[0-9a-f]{64}$/;

function validate(payload) {
  const violations = [];
  if (typeof payload !== "object" || payload === null || Array.isArray(payload)) {
    return ["payload: not an object"];
  }
  for (const field of REQUIRED) {
    if (!(field in payload)) violations.push(`${field}: missing required field`);
  }
  for (const field of ["workflow_id", "unit_id"]) {
    if (field in payload && (typeof payload[field] !== "string" || payload[field] === "")) {
      violations.push(`${field}: must be a non-empty string`);
    }
  }
  for (const field of ["receipt_sha256", "history_sha256"]) {
    if (field in payload && (typeof payload[field] !== "string" || !SHA256.test(payload[field]))) {
      violations.push(`${field}: must be a 64-char lowercase hex sha256`);
    }
  }
  if ("receipt_count" in payload) {
    const v = payload.receipt_count;
    if (!Number.isInteger(v) || v < 0) violations.push("receipt_count: must be an integer >= 0");
  }
  if ("unknown_outcomes" in payload && !Array.isArray(payload.unknown_outcomes)) {
    violations.push("unknown_outcomes: must be an array");
  }
  for (const key of Object.keys(payload)) {
    if (!REQUIRED.includes(key)) violations.push(`${key}: additional property not allowed`);
  }
  return violations;
}

const payload = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
process.stdout.write(JSON.stringify(validate(payload)) + "\n");
