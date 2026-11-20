const puppeteer = require('puppeteer');
const fs = require('fs');

const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const DEEPSEEK_BASE = 'https://chat.deepseek.com/';

(async () => {
  const browser = await puppeteer.launch({
    headless: false,                      // visible browser
    executablePath: CHROMIUM_PATH,
    userDataDir: './browser-data',        // same dir used by headless script
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
  console.log('👉 Please log in manually (including PassKey if needed).');
  console.log('   Once you reach the chat page, press Ctrl+C in this terminal.');
  console.log('   (Or just close the browser window.)');

  // Wait indefinitely until the user interrupts
  process.stdin.resume();
  process.on('SIGINT', async () => {
    console.log('✅ Profile saved. You can now use deepseek.js headless.');
    await browser.close();
    process.exit();
  });
})();
