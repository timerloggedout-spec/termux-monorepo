import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const COOKIES_FILE = path.resolve(process.argv[2] || './cookies_2.json');
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';

const cookiesRaw = JSON.parse(fs.readFileSync(COOKIES_FILE, 'utf-8'));
const cookies = Array.isArray(cookiesRaw) ? cookiesRaw : (cookiesRaw.cookies || []);

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

let capturedToken = null;

const browser = await puppeteer.launch({
  headless: 'new',
  executablePath: CHROMIUM_PATH,
  args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu']
});

const page = await browser.newPage();

// Intercept API requests
page.on('request', req => {
  const auth = req.headers()['authorization'];
  if (auth && auth.startsWith('Bearer ') && !capturedToken) {
    capturedToken = auth.replace('Bearer ', '');
    console.log('🔑 Token captured from:', req.url());
  }
});

// SET COOKIES ON A BLANK PAGE FIRST (no prior navigation)
await page.goto('about:blank');
await page.setCookie(...cookieParams);
console.log('🍪 Cookies set on blank page.');

// Now navigate to DeepSeek
await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });
console.log('📍 Navigated to chat page.');
await new Promise(r => setTimeout(r, 3000));

// If no token, force an API call
if (!capturedToken) {
  console.log('⏳ Triggering API call...');
  await page.evaluate(async () => {
    await fetch('/api/v0/chat_session/fetch_page');
  });
  await new Promise(r => setTimeout(r, 2000));
}

if (capturedToken) {
  console.log('TOKEN:' + capturedToken);
  fs.writeFileSync(path.join(__dirname, 'token_account2.txt'), capturedToken);
  console.log('✅ Token saved.');
} else {
  console.log('❌ No token captured. Page:', page.url());
  process.exit(1);
}

await browser.close();
