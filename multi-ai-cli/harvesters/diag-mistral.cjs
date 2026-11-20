#!/usr/bin/env node
// Quick diagnostic: are we logged in? What's on the page?
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const COOKIES_FILE = path.join(process.env.HOME, '.multi-ai-tokens', 'mistral_cookies.json');

(async () => {
  const ffData = JSON.parse(fs.readFileSync(COOKIES_FILE, 'utf-8'));
  const ffCookies = ffData.cookies || ffData;
  const chromiumCookies = ffCookies.map(c => ({
    name: c.name, value: c.value,
    domain: c.domain.startsWith('.') ? c.domain.substring(1) : c.domain,
    path: c.path || '/',
    httpOnly: c.httpOnly || false,
    secure: c.secure || false,
    sameSite: c.sameSite === 'no_restriction' ? 'None' : c.sameSite === 'lax' ? 'Lax' : 'Strict',
    expires: c.expirationDate ? Math.round(c.expirationDate) : Math.round(Date.now()/1000)+86400*365,
  }));

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  await page.setCookie(...chromiumCookies);
  await page.goto('https://chat.mistral.ai', { waitUntil: 'networkidle0', timeout: 60000 });
  await new Promise(r => setTimeout(r, 3000));

  // Check page state
  const title = await page.title();
  const bodyText = await page.evaluate(() => document.body.innerText.slice(0, 500));
  console.log('Title:', title);
  console.log('Body (first 500):', bodyText);

  // Look for chat input
  const selectors = ['textarea', 'textarea[name="message.text"]', 'div[contenteditable="true"]', '[data-testid="chat-input"]', '[aria-label="Message"]'];
  for (const sel of selectors) {
    const el = await page.$(sel);
    console.log(`Selector "${sel}": ${el ? 'FOUND' : 'not found'}`);
  }

  // Look for login/signup indicators
  const loginBtn = await page.$('a[href*="login"], button:has-text("Log in"), button:has-text("Sign up"), a:has-text("Sign in")');
  console.log('Login/Signup elements:', loginBtn ? 'FOUND (NOT AUTHENTICATED)' : 'none (likely authenticated)');

  // Try to get localStorage token
  const localToken = await page.evaluate(() => localStorage.getItem('userToken'));
  console.log('localStorage userToken:', localToken);

  await page.screenshot({ path: path.join(process.env.HOME, '.multi-ai-tokens', 'mistral_diag.png') });
  console.log('Screenshot saved to ~/.multi-ai-tokens/mistral_diag.png');
  await browser.close();
  process.exit(0);
})();
