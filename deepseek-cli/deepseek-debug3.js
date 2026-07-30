const puppeteer = require('puppeteer');
const fs = require('fs');

const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const FIREFOX_UA = 'Mozilla/5.0 (Android 14; Mobile; rv:150.0) Gecko/150.0 Firefox/150.0';
const DEEPSEEK_BASE = 'https://chat.deepseek.com/';
const DOWNLOADS_DIR = '/data/data/com.termux/files/home/storage/downloads';

const wait = (ms) => new Promise(r => setTimeout(r, ms));

(async () => {
  // 1. Find latest cookies*.json
  const files = fs.readdirSync(DOWNLOADS_DIR).filter(f => f.startsWith('cookies') && f.endsWith('.json'));
  if (files.length === 0) {
    console.error('❌ No cookies*.json files found in', DOWNLOADS_DIR);
    process.exit(1);
  }
  files.sort((a, b) => {
    const statA = fs.statSync(`${DOWNLOADS_DIR}/${a}`);
    const statB = fs.statSync(`${DOWNLOADS_DIR}/${b}`);
    return statB.mtimeMs - statA.mtimeMs;
  });
  const latest = `${DOWNLOADS_DIR}/${files[0]}`;
  console.log('📁 Latest cookies file:', files[0]);

  // 2. Extract cookies array
  const raw = JSON.parse(fs.readFileSync(latest, 'utf-8'));
  const cookies = raw.cookies || raw; // fallback if already array
  if (!Array.isArray(cookies)) {
    console.error('❌ Cookies file does not contain an array or .cookies field.');
    process.exit(1);
  }

  // 3. Convert to Puppeteer format, logging each
  const cookieParams = cookies.map((c, i) => {
    const cookie = {
      name: c.name,
      value: c.value,
      domain: c.hostOnly ? c.domain.replace(/^\./, '') : c.domain, // strip leading dot if hostOnly
      path: c.path || '/',
      httpOnly: c.httpOnly ?? false,
      secure: c.secure ?? true,
      sameSite: (c.sameSite || 'Lax').toLowerCase(),
      expires: c.expirationDate && c.expirationDate > 0 ? c.expirationDate : -1,
    };
    // Normalize sameSite: valid values: Strict|Lax|None; unspecified -> Lax
    const valid = ['strict','lax','none'];
    if (!valid.includes(cookie.sameSite)) cookie.sameSite = 'lax';
    cookie.sameSite = cookie.sameSite.charAt(0).toUpperCase() + cookie.sameSite.slice(1);
    // If the cookie was originally secure but now we removed url, ensure secure flag matches
    if (cookie.secure === undefined) cookie.secure = true;
    console.log(`  🍪 Setting cookie [${i}]: ${cookie.name} (domain: ${cookie.domain}, secure: ${cookie.secure}, sameSite: ${cookie.sameSite}, httpOnly: ${cookie.httpOnly})`);
    return cookie;
  });

  // 4. Launch browser
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    userDataDir: './browser-data',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      `--user-agent=${FIREFOX_UA}`,
    ],
  });

  const page = await browser.newPage();
  await page.setUserAgent(FIREFOX_UA);
  await page.setExtraHTTPHeaders({ 'Accept-Language': 'en-US,en;q=0.9' });

  try {
    // 5. Go to a non-secure page? No, go to base secure page.
    console.log('🌐 Visiting base domain to set cookies...');
    await page.goto(DEEPSEEK_BASE, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.setCookie(...cookieParams);
    await wait(1000);
    // Check cookies immediately after setting
    const cookiesAfterSet = await page.cookies();
    console.log('🔍 Cookies in jar after setting:', cookiesAfterSet.map(c => c.name).join(', '));

    // Save screenshot of the sign-in page (will be useful)
    await page.screenshot({ path: 'debug3-after-set.png' });

    // 6. Now try to go to the chat
    console.log(`➡️ Navigating to ${DEEPSEEK_BASE}`);
    await page.goto(DEEPSEEK_BASE, { waitUntil: 'networkidle2', timeout: 30000 });
    await wait(2000);

    // Save screenshot of current page
    await page.screenshot({ path: 'debug3-current.png' });
    console.log('📸 debug3-current.png saved (opens the page you land on)');

    // Log final URL
    const finalUrl = page.url();
    console.log('📍 Final URL:', finalUrl);

    // If still sign-in, dump cookies and page text
    if (finalUrl.includes('/sign_in')) {
      console.log('❌ Still on sign-in. Dumping cookies and page text...');
      const allCookies = await page.cookies();
      console.log('🍪 Cookies present:', JSON.stringify(allCookies.map(c => ({name:c.name, domain:c.domain, value: c.value.substring(0,10)+'...'})), null, 2));
      const bodyText = await page.evaluate(() => document.body.innerText);
      console.log('📝 Page text (first 300 chars):', bodyText.substring(0, 300));
    } else {
      console.log('✅ Successfully reached chat!');
    }

  } catch (err) {
    console.error('💥 Error:', err.message);
  } finally {
    await browser.close();
  }
})();
