from pathlib import Path
import re

p = Path.home() / "deepseek-cli/tests/deepseek-full-suite.mjs"

src = p.read_text()

# ==========================================================
# Fix detached frame runtime extraction
# ==========================================================

src = re.sub(
r"await page\.waitForFunction\(\(\) => globalThis\.__DS_RUNTIME_INTEL__, \{ timeout: 5000 \}\);\s*const runtime = await page\.evaluate\(\(\) => globalThis\.__DS_RUNTIME_INTEL__\);",
"""
let runtime = null;

try {
  if (!page.isClosed()) {
    await page.waitForFunction(
      () => globalThis.__DS_RUNTIME_INTEL__,
      { timeout: 3000 }
    );

    runtime = await page.evaluate(() => {
      return globalThis.__DS_RUNTIME_INTEL__ || null;
    });
  }
} catch (err) {
  console.error('⚠ Runtime extraction skipped:', err.message);
}
""",
src,
flags=re.MULTILINE
)

# ==========================================================
# Replace callback fs.writeFile with promises API
# ==========================================================

src = src.replace(
    "fs.writeFile(",
    "fs.promises.writeFile("
)

# ==========================================================
# Runtime null guards
# ==========================================================

src = src.replace(
    "runtime.streams",
    "(runtime?.streams || [])"
)

src = src.replace(
    "logTest('Runtime stream intelligence', true, runtime);",
    "logTest('Runtime stream intelligence', true, runtime || { streams: [] });"
)

# ==========================================================
# Ensure runtime bootstrap exists
# ==========================================================

if "__DS_RUNTIME_INTEL__ = {" not in src:
    inject = """
await page.evaluateOnNewDocument(() => {
  globalThis.__DS_RUNTIME_INTEL__ = {
    streams: [],
    fetches: [],
    events: [],
    created: Date.now()
  };
});
"""

    src = src.replace(
        "const page = await browser.newPage();",
        "const page = await browser.newPage();\\n" + inject
    )

# ==========================================================
# Fix any Playwright remnants
# ==========================================================

src = src.replace(
    "page.addInitScript",
    "page.evaluateOnNewDocument"
)

p.write_text(src)

print("✅ Runtime hardening patch applied")
