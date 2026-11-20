#!/usr/bin/env node
// archw1z Mistral token harvester — single headless launch
// Loads Firefox cookies, navigates to chat.mistral.ai,
// lets browser solve JS challenge, intercepts Bearer token
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const COOKIES_FILE = path.join(process.env.HOME, '.multi-ai-tokens', 'mistral_cookies.json');
const TOKEN_OUT = path.join(process.env.HOME, '.multi-ai-tokens', 'mistral_token.txt');
const CHROMIUM_COOKIES_OUT = path.join(process.env.HOME, '.multi-ai-tokens', 'mistral_chromium_cookies.json');

(async () => {
  // Load Firefox cookies
  const ffData = JSON.parse(fs.readFileSync(COOKIES_FILE, 'utf-8'));
  const ffCookies = ffData.cookies || ffData;

  // Convert Firefox cookie format to Chromium cookie format
  const chromiumCookies = ffCookies.map(c => ({
    name: c.name,
    value: c.value,
    domain: c.domain.startsWith('.') ? c.domain.substring(1) : c.domain,
    path: c.path || '/',
    httpOnly: c.httpOnly || false,
    secure: c.secure || false,
    sameSite: c.sameSite === 'no_restriction' ? 'None' :
              c.sameSite === 'lax' ? 'Lax' :
              c.sameSite === 'strict' ? 'Strict' : 'Lax',
    expires: c.expirationDate ? Math.round(c.expirationDate) :
             Math.round(Date.now() / 1000) + 86400 * 365,
  }));

  console.log(`🍪 Loaded ${chromiumCookies.length} Firefox cookies`);

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });

  const page = await browser.newPage();
  let capturedToken = null;

  // Intercept ALL requests to capture Bearer token
  await page.setRequestInterception(true);
  page.on('request', async (req) => {
    const auth = req.headers()['authorization'];
    if (auth && auth.startsWith('Bearer ') && !capturedToken) {
      capturedToken = auth.replace('Bearer ', '');
      console.log('🔥 Captured Mistral Bearer token!');
    }
    // Also watch for X-CSRFToken header (needed for API calls)
    req.continue();
  });

  // Set cookies BEFORE navigation
  await page.setCookie(...chromiumCookies);
  console.log('🍪 Cookies set in Chromium');

  // Navigate — browser will solve JS challenge automatically
  console.log('🌐 Navigating to https://chat.mistral.ai ...');
  await page.goto('https://chat.mistral.ai', {
    waitUntil: 'networkidle0',
    timeout: 60000,
  });

  console.log('📄 Page loaded. Waiting for API calls...');
  // Wait for JS challenge to solve and API to start making requests
  await new Promise(r => setTimeout(r, 10000));

  // If no token yet, try navigating to trigger API calls
  if (!capturedToken) {
    console.log('⏳ No token yet — sending a test prompt to trigger API...');
    try {
      await page.waitForSelector('textarea[name="message.text"]', { timeout: 10000 });
      await page.type('textarea[name="message.text"]', 'Hello');
      await page.waitForSelector('button[type="submit"]', { timeout: 5000 });
      await page.click('button[type="submit"]');
      await new Promise(r => setTimeout(r, 8000)); // wait for API request
    } catch (e) {
      console.log('⚠️ Could not interact with page:', e.message);
    }
  }

  // Save Chromium cookies (fresh after JS challenge)
  const chromCookies = await page.cookies();
  fs.writeFileSync(CHROMIUM_COOKIES_OUT, JSON.stringify(chromCookies, null, 2));
  console.log(`💾 Chromium cookies saved (${chromCookies.length})`);

  if (capturedToken) {
    fs.writeFileSync(TOKEN_OUT, capturedToken);
    console.log('✅ Mistral token saved!');
    console.log(`   Token: ${capturedToken.substring(0, 30)}...`);
  } else {
    console.log('❌ No token captured.');
    console.log('   Try opening the page manually to verify cookies are valid.');
    console.log('   Page URL:', page.url());
    // Take screenshot for debugging
    await page.screenshot({ path: path.join(process.env.HOME, '.multi-ai-tokens', 'mistral_debug.png') });
    console.log('   Screenshot saved to ~/.multi-ai-tokens/mistral_debug.png');
  }

  await browser.close();
  process.exit(0);
})();
