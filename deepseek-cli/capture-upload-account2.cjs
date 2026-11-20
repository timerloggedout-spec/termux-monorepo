const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const USER_DATA_DIR = './browser-data-account2-v2';
const INPUT_SEL = 'textarea[placeholder="Message DeepSeek"]';
const PAPERCLIP_SEL = '.f02f0e25';

const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  // Create a test file for upload
  const testFile = path.join(__dirname, 'upload-test.txt');
  fs.writeFileSync(testFile, 'Account2 token capture test', 'utf8');

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    userDataDir: USER_DATA_DIR,
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu'],
  });

  const page = await browser.newPage();

  // Intercept upload request to grab the Authorization header
  let capturedToken = null;
  page.on('request', req => {
    if (req.url().includes('/api/v0/file/upload_file')) {
      const auth = req.headers()['authorization'];
      if (auth && auth.startsWith('Bearer ')) {
        capturedToken = auth.replace('Bearer ', '');
        console.log('🔑 Token captured from upload request');
      }
    }
  });

  try {
    await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });
    console.log('📍 Page URL:', page.url());

    if (page.url().includes('/sign_in')) {
      console.log('❌ Not authenticated');
      process.exit(1);
    }

    console.log('✅ Authenticated as Account 2');

    // Wait for input
    await page.waitForSelector(INPUT_SEL, { timeout: 10000 });

    // Click paperclip and upload the test file to trigger an API call
    const paperclip = await page.$(PAPERCLIP_SEL);
    if (paperclip) {
      const [fileChooser] = await Promise.all([
        page.waitForFileChooser({ timeout: 10000 }),
        paperclip.click()
      ]);
      await fileChooser.accept([testFile]);
      console.log('📎 Upload triggered...');
      await wait(4000);
    } else {
      // Fallback: send a quick message to trigger a completion
      console.log('⚠️ Paperclip not found, sending a message instead...');
      await page.type(INPUT_SEL, 'Token capture test');
      await page.keyboard.press('Enter');
      await wait(5000);
    }

    if (capturedToken) {
      console.log('TOKEN:' + capturedToken);
      fs.writeFileSync(path.join(__dirname, 'token_account2.txt'), capturedToken);
      console.log('✅ Token saved to token_account2.txt');
    } else {
      console.log('❌ No token captured');
      process.exit(1);
    }
  } finally {
    try { fs.unlinkSync(testFile); } catch {}
    await browser.close();
  }
})();
