const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const INPUT_SEL = 'textarea[placeholder="Message DeepSeek"]';
const INSTANT_RADIO_SEL = 'div[data-model-type="default"][role="radio"]';
const DOWNLOADS_DIR = path.join(process.env.HOME, 'storage/downloads');

const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    userDataDir: './browser-data',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu'],
  });

  const page = await browser.newPage();
  const networkLog = [];

  // Log ALL requests after we start watching
  await page.setRequestInterception(true);
  page.on('request', req => {
    networkLog.push({
      url: req.url(),
      method: req.method(),
      headers: req.headers(),
      postData: req.hasPostData() ? req.postData()?.substring(0, 3000) : null
    });
    req.continue();
  });

  // Also log responses to get status codes
  const responseLog = [];
  page.on('response', async resp => {
    responseLog.push({
      url: resp.url(),
      status: resp.status()
    });
  });

  try {
    await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2' });
    if (page.url().includes('/sign_in')) {
      console.log('❌ Not authenticated.');
      await browser.close();
      process.exit(1);
    }
    await page.waitForSelector(INPUT_SEL);

    // Switch to Instant
    const instantRadio = await page.$(INSTANT_RADIO_SEL);
    if (instantRadio) {
      const checked = await page.evaluate(el => el.getAttribute('aria-checked'), instantRadio);
      if (checked !== 'true') await instantRadio.click();
      await wait(800);
    }

    // Type a character to reveal send/upload bar
    const input = await page.$(INPUT_SEL);
    await input.click();
    await page.type(INPUT_SEL, 'x', { delay: 10 });
    await wait(500);

    // Click the paperclip button (f02f0e25) to open file picker
    const paperclip = await page.$('.f02f0e25');
    if (paperclip) {
      await paperclip.click();
      await wait(500);
      console.log('📎 Paperclip clicked.');
    }

    // Create test file
    const testFilePath = path.join(__dirname, 'test-upload.txt');
    fs.writeFileSync(testFilePath, 'hello from deepseek cli', 'utf8');

    // Get the file input and upload
    const fileInput = await page.$('input[type="file"]');
    if (!fileInput) {
      console.log('❌ No file input found after paperclip click.');
      await browser.close();
      return;
    }

    // Use evaluate to manually trigger change event after setting file
    await fileInput.uploadFile(testFilePath);
    // Dispatch a change event explicitly to ensure React picks it up
    await page.evaluate(() => {
      const input = document.querySelector('input[type="file"]');
      if (input) {
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
    console.log('📤 File uploaded and change event dispatched.');
    await wait(5000); // give time for upload request to fire

    // Remove test file
    fs.unlinkSync(testFilePath);

    // Write network logs
    const logPath = path.join(DOWNLOADS_DIR, 'network-log.json');
    fs.writeFileSync(logPath, JSON.stringify({ requests: networkLog, responses: responseLog }, null, 2));
    console.log('📝 Network log saved to', logPath);
    console.log(`   ${networkLog.length} requests and ${responseLog.length} responses captured.`);

    // Quick summary: look for upload-like requests
    const uploadCandidates = networkLog.filter(r => 
      r.url.includes('upload') || r.url.includes('file') || r.url.includes('attachment') ||
      (r.method === 'POST' && r.postData && r.postData.includes('hello'))
    );
    console.log('🔍 Upload candidates:', uploadCandidates.map(r => r.url));

  } catch (e) {
    console.error(e);
  } finally {
    await browser.close();
  }
})();
