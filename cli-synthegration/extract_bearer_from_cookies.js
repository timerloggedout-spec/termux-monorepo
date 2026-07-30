const puppeteer = require('puppeteer');
const fs = require('fs');
const COOKIES_FILE = process.argv[2] || 'cookies_2.json';
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';

(async () => {
  const raw = fs.readFileSync(COOKIES_FILE, 'utf8');
  const data = JSON.parse(raw);
  const cookies = Array.isArray(data) ? data : (data.cookies || []);
  // Convert to Chromium cookie format
  const chromeCookies = cookies.map(c => ({
    name: c.name,
    value: c.value,
    domain: c.domain,
    path: c.path || '/',
    httpOnly: c.httpOnly || false,
    secure: c.secure || true,
    sameSite: 'None',
    expires: c.expirationDate ? Math.floor(c.expirationDate) : undefined
  }));

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu']
  });
  const page = await browser.newPage();

  let token = null;
  page.on('request', req => {
    if (req.url().includes('/api/v0/')) {
      const auth = req.headers()['authorization'];
      if (auth && auth.startsWith('Bearer ')) {
        token = auth.replace('Bearer ', '');
      }
    }
  });

  // Set cookies for chat.deepseek.com before navigating
  for (const c of chromeCookies) {
    if (c.domain && c.domain.includes('deepseek.com')) {
      await page.setCookie(c);
    }
  }
  // Also set cookies from all domains (some might be needed)
  await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });

  // If not captured yet, manually trigger an API call
  if (!token) {
    try {
      await page.evaluate(() => fetch('/api/v0/chat_session/fetch_page'));
      await page.waitForTimeout(3000);
    } catch {}
  }

  // Last resort: localStorage
  if (!token) {
    token = await page.evaluate(() => localStorage.getItem('userToken'));
  }

  await browser.close();
  if (token) {
    console.log(token);
  } else {
    console.error('No token found');
    process.exit(1);
  }
})();
