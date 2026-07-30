const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const INPUT_SEL = 'textarea[placeholder="Message DeepSeek"]';
const INSTANT_RADIO_SEL = 'div[data-model-type="default"][role="radio"]';
const PAPERCLIP_SEL = '.f02f0e25';

const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  // Create a test file
  const testFile = path.join(__dirname, 'upload-test.txt');
  fs.writeFileSync(testFile, 'Hello from capture script', 'utf8');

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    userDataDir: './browser-data',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu'],
  });

  const page = await browser.newPage();

  // Intercept all requests – we only care about the upload
  const captured = { uploadRequest: null, uploadResponse: null };

  await page.setRequestInterception(true);
  page.on('request', (req) => {
    if (req.url().includes('/api/v0/file/upload_file')) {
      captured.uploadRequest = {
        url: req.url(),
        method: req.method(),
        headers: req.headers(),
        postData: req.hasPostData() ? req.postData() : null
      };
    }
    req.continue();
  });

  page.on('response', async (resp) => {
    if (resp.url().includes('/api/v0/file/upload_file') && resp.request().method() === 'POST') {
      try {
        captured.uploadResponse = {
          status: resp.status(),
          headers: resp.headers(),
          body: await resp.text()
        };
      } catch {}
    }
  });

  try {
    // Go to a fresh chat
    await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });
    if (page.url().includes('/sign_in')) {
      console.log('❌ Not authenticated. Run manual login first.');
      process.exit(1);
    }
    await page.waitForSelector(INPUT_SEL, { timeout: 10000 });
    console.log('✅ Authenticated.');

    // Switch to Instant mode (toggle must be visible – new chat)
    const instantRadio = await page.$(INSTANT_RADIO_SEL);
    if (instantRadio) {
      const checked = await page.evaluate(el => el.getAttribute('aria-checked'), instantRadio);
      if (checked !== 'true') {
        await instantRadio.click();
        await wait(800);
        console.log('🔹 Switched to Instant mode.');
      }
    } else {
      console.log('⚠️ Instant radio not found. Continuing anyway.');
    }

    // Click paperclip and use file chooser
    const paperclip = await page.$(PAPERCLIP_SEL);
    if (!paperclip) {
      console.log('❌ Paperclip button not found.');
      process.exit(1);
    }

    const [fileChooser] = await Promise.all([
      page.waitForFileChooser({ timeout: 10000 }),
      paperclip.click()
    ]);
    await fileChooser.accept([testFile]);
    console.log('📎 File selected. Waiting for upload to complete...');
    await wait(3000); // let the upload request happen

    // Write captured data to file
    fs.writeFileSync('upload-api.json', JSON.stringify(captured, null, 2));
    console.log('✅ upload-api.json saved.');
    console.log('Request URL:', captured.uploadRequest?.url || 'not captured');
    console.log('Response status:', captured.uploadResponse?.status || 'not captured');

  } catch (e) {
    console.error(e);
  } finally {
    // Clean up test file
    try { fs.unlinkSync(testFile); } catch {}
    await browser.close();
  }
})();
