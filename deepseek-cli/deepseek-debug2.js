const puppeteer = require('puppeteer');
const fs = require('fs');

const COOKIES_FILE = './cookies.json';
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const DEEPSEEK_BASE = 'https://chat.deepseek.com/';
const SESSION = process.argv[2] || '';

const wait = (ms) => new Promise(r => setTimeout(r, ms));

(async () => {
  const cookies = JSON.parse(fs.readFileSync(COOKIES_FILE, 'utf-8'));
  const cookieParams = cookies.map(c => ({
    name: c.name,
    value: c.value,
    domain: c.domain,
    path: c.path || '/',
    expires: c.expirationDate || -1,
    httpOnly: c.httpOnly || false,
    secure: c.secure || false,
    sameSite: c.sameSite || 'Lax',
  }));

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    userDataDir: './browser-data',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
  });

  const page = await browser.newPage();

  try {
    // 1. First visit the base domain to establish cookie context
    console.log('👉 Visiting base domain to set cookies...');
    await page.goto(DEEPSEEK_BASE, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.setCookie(...cookieParams);
    console.log('🍪 Cookies set.');

    // 2. Now navigate to the session (or stay on new chat if no session)
    const targetUrl = SESSION ? `${DEEPSEEK_BASE}a/chat/s/${SESSION}` : DEEPSEEK_BASE;
    console.log(`👉 Navigating to ${targetUrl}`);
    await page.goto(targetUrl, { waitUntil: 'networkidle2', timeout: 30000 });
    await wait(2000);

    // 3. Log what we actually see
    const finalUrl = page.url();
    const title = await page.title();
    console.log(`📍 Final URL: ${finalUrl}`);
    console.log(`📄 Title: ${title}`);

    // Screenshot
    await page.screenshot({ path: 'debug2-screenshot.png', fullPage: false });
    console.log('✅ debug2-screenshot.png saved');

    // Page text snippet
    const bodyText = await page.evaluate(() => document.body.innerText);
    console.log('📝 Page text (first 500 chars):', bodyText.substring(0, 500));

    // Input elements again
    const inputInfo = await page.evaluate(() => {
      const inputs = Array.from(document.querySelectorAll(
        'textarea, input[type="text"], [contenteditable="true"], [role="textbox"]'
      ));
      return inputs.map(el => ({
        tag: el.tagName,
        placeholder: el.placeholder || el.getAttribute('placeholder') || '',
        ariaLabel: el.getAttribute('aria-label') || '',
        role: el.getAttribute('role') || '',
      }));
    });
    console.log('📥 Input elements found:', JSON.stringify(inputInfo, null, 2));

  } catch (err) {
    console.error('❌ Debug error:', err.message);
  } finally {
    await browser.close();
  }
})();
