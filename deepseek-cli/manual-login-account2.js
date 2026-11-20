const puppeteer = require('puppeteer');
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';

(async () => {
  const browser = await puppeteer.launch({
    headless: false,
    executablePath: CHROMIUM_PATH,
    userDataDir: './browser-data-account2',   // <-- separate profile
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu']
  });
  const page = await browser.newPage();
  await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2' });
  console.log('👉 Log in with Account 2. Press Ctrl+C when you reach the chat page.');
  process.stdin.resume();
  process.on('SIGINT', async () => {
    await browser.close();
    console.log('✅ Account 2 profile saved.');
    process.exit();
  });
})();
