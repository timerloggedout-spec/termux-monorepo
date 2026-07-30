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
    const url = SESSION ? `${DEEPSEEK_BASE}a/chat/s/${SESSION}` : DEEPSEEK_BASE;
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.setCookie(...cookieParams);
    await page.reload({ waitUntil: 'networkidle2', timeout: 30000 });

    // Wait 3 seconds for JS to render
    await wait(3000);

    // Screenshot
    await page.screenshot({ path: 'debug-screenshot.png', fullPage: false });
    console.log('✅ Screenshot saved to debug-screenshot.png');

    // Page text
    const bodyText = await page.evaluate(() => document.body.innerText);
    fs.writeFileSync('debug-page-text.txt', bodyText.substring(0, 2000));
    console.log('✅ Page text (first 2000 chars) saved to debug-page-text.txt');

    // HTML snippet
    const html = await page.content();
    fs.writeFileSync('debug-page-html.txt', html.substring(0, 5000));
    console.log('✅ HTML snippet saved to debug-page-html.txt');

    // Find all input elements
    const inputInfo = await page.evaluate(() => {
      const inputs = Array.from(document.querySelectorAll(
        'textarea, input[type="text"], [contenteditable="true"], [role="textbox"]'
      ));
      return inputs.map(el => ({
        tag: el.tagName,
        placeholder: el.placeholder || el.getAttribute('placeholder') || '',
        contentEditable: el.contentEditable,
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
