// Lightweight cookie harvester – reuses your existing capture pattern
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const OUT = path.join(process.env.HOME, '.multi-ai-tokens', 'mistral_cookies.json');

(async () => {
  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox'] });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('🌐 Navigate to https://chat.mistral.ai, log in, then press Enter here...');
  await page.goto('https://chat.mistral.ai', { waitUntil: 'domcontentloaded' });

  process.stdin.setRawMode(true);
  await new Promise(resolve => process.stdin.once('data', resolve));

  const cookies = await context.cookies();
  fs.writeFileSync(OUT, JSON.stringify(cookies, null, 2));
  console.log(`✅ Cookies saved to ${OUT}`);
  await browser.close();
  process.exit(0);
})();
