const puppeteer = require('puppeteer');
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({
    headless: false,                    // visible, to interact
    executablePath: CHROMIUM_PATH,
    userDataDir: './browser-data',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu'],
  });
  const page = await browser.newPage();
  await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });
  await wait(2000);
  if (page.url().includes('/sign_in')) { console.log('❌ Auth required'); return; }
  console.log('✅ Logged in. Now manually:');
  console.log('1. Open any existing chat.');
  console.log('2. Click the edit pencil on a user message.');
  console.log('3. Look for any new buttons (like "Save & submit", "Branch", "Fork").');
  console.log('4. Press Enter in this terminal to dump the DOM...');
  await new Promise(r => process.stdin.once('data', r));
  // Dump all buttons and their classes/text
  const info = await page.evaluate(() => {
    const buttons = document.querySelectorAll('button, [role="button"]');
    return Array.from(buttons).map(b => ({
      text: b.innerText?.trim().substring(0, 50),
      classes: b.className,
      ariaLabel: b.getAttribute('aria-label'),
    }));
  });
  console.log(JSON.stringify(info, null, 2));
  await browser.close();
})();
