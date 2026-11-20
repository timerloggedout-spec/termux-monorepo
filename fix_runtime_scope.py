from pathlib import Path

p = Path('tests/deepseek-full-suite.mjs')
s = p.read_text()

# -------------------------------------------------
# 1. Promote runtime to outer scope
# -------------------------------------------------

old = """  try {



  try {

  let runtime = null;
"""

new = """  let runtime = null;

  try {



  try {
"""

s = s.replace(old, new)

# -------------------------------------------------
# 2. Harden runtime summary logging
# -------------------------------------------------

old = """    console.log(JSON.stringify({
      fetches: runtime?.fetches.length,
      streams: (runtime?.streams || []).length,
      completions: runtime?.completions.length,
      uploads: runtime?.uploads.length
    }, null, 2));
"""

new = """    console.log(JSON.stringify({
      fetches: (runtime?.fetches || []).length,
      streams: (runtime?.streams || []).length,
      wsMessages: (runtime?.wsMessages || []).length,
      domMutations: (runtime?.domMutations || []).length,
      lastStream: !!runtime?.lastStream
    }, null, 2));
"""

s = s.replace(old, new)

# -------------------------------------------------
# 3. Ensure runtime fallback matches exporter shape
# -------------------------------------------------

old = """  runtime = runtime || {
    streams: [],
    fetches: [],
    events: [],
    recovered: true
  };
"""

new = """  runtime = runtime || {
    streams: [],
    fetches: [],
    wsMessages: [],
    domMutations: [],
    lastStream: null,
    recovered: true
  };
"""

s = s.replace(old, new)

p.write_text(s)

print("✅ Runtime scope + telemetry hardening applied")
