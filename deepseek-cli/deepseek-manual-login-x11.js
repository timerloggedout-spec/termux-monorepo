const puppeteer = require('puppeteer');
const DEEPSEEK_BASE = 'https://chat.deepseek.com/';
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';

(async () => {
  const browser = await puppeteer.launch({
    headless: false,                      // visible window
    executablePath: CHROMIUM_PATH,
    userDataDir: './browser-data',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--disable-blink-features=AutomationControlled',
    ],
    ignoreDefaultArgs: ['--enable-automation'],
  });

  const page = await browser.newPage();
  await page.goto(DEEPSEEK_BASE, { waitUntil: 'networkidle2' });
  console.log('👉 Log in now (use PassKey if needed).');
  console.log('   Once you see the chat page, press Ctrl+C here.');
  process.stdin.resume();
  process.on('SIGINT', async () => {
    await browser.close();
    console.log('✅ Profile saved. You can now run deepseek.js.');
    process.exit();
  });
})();
