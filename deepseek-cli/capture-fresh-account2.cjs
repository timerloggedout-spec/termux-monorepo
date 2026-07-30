const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const COOKIES_FILE = process.argv[2] || './cookies_2.json';
const USER_DATA_DIR = './browser-data-account2-fresh';
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const PAPERCLIP_SEL = '.f02f0e25';

const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const cookiesRaw = JSON.parse(fs.readFileSync(COOKIES_FILE, 'utf-8'));
  const cookies = Array.isArray(cookiesRaw) ? cookiesRaw : (cookiesRaw.cookies || []);
  const cookieParams = cookies.map(c => ({
    name: c.name, value: c.value, domain: c.domain,
    path: c.path || '/', expires: c.expirationDate || -1,
    httpOnly: c.httpOnly || false, secure: c.secure || false,
    sameSite: c.sameSite || 'Lax',
  }));

  const testFile = path.join(__dirname, 'upload-test.txt');
  fs.writeFileSync(testFile, 'Account2 fresh capture', 'utf8');

  let capturedToken = null;
  const browser = await puppeteer.launch({
    headless: 'new', executablePath: CHROMIUM_PATH,
    userDataDir: USER_DATA_DIR,
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu']
  });

  const page = await browser.newPage();

  // Intercept upload requests for Bearer token
  page.on('request', req => {
    if (req.url().includes('/api/v0/file/upload_file')) {
      const auth = req.headers()['authorization'];
      if (auth && auth.startsWith('Bearer ') && !capturedToken) {
        capturedToken = auth.replace('Bearer ', '');
        console.log('🔑 Token captured from upload request');
      }
    }
  });

  // SET COOKIES ON BLANK PAGE FIRST
  await page.goto('about:blank');
  await page.setCookie(...cookieParams);
  console.log('🍪 ' + cookieParams.length + ' cookies set on blank page.');

  // Navigate to chat
  await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });
  console.log('📍 Page URL:', page.url());

  if (page.url().includes('/sign_in')) {
    console.log('❌ Still sign-in. Session expired.');
    process.exit(1);
  }

  console.log('✅ Authenticated! Capturing token...');

  // Wait for textarea
  await page.waitForSelector('textarea[placeholder="Message DeepSeek"]', { timeout: 10000 });

  // Trigger upload for token capture
  const paperclip = await page.$(PAPERCLIP_SEL);
  if (paperclip) {
    const [fileChooser] = await Promise.all([
      page.waitForFileChooser({ timeout: 10000 }),
      paperclip.click()
    ]);
    await fileChooser.accept([testFile]);
    console.log('📎 Upload triggered...');
    await wait(5000);
  } else {
    console.log('⚠️ Paperclip not found, sending message...');
    await page.type('textarea', 'Token capture');
    await page.keyboard.press('Enter');
    await wait(5000);
  }

  if (capturedToken) {
    console.log('TOKEN:' + capturedToken);
    fs.writeFileSync(path.join(__dirname, 'token_account2.txt'), capturedToken);
    console.log('✅ Account 2 token saved.');
  } else {
    console.log('❌ No token captured');
    process.exit(1);
  }

  try { fs.unlinkSync(testFile); } catch {}
  await browser.close();
})();
