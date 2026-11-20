const puppeteer = require('puppeteer');
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const DEEPSEEK_BASE = 'https://chat.deepseek.com/';
const INPUT_SEL = 'textarea[placeholder="Message DeepSeek"]';
const SEND_BTN_SEL = '._52c986b';

const wait = ms => new Promise(r => setTimeout(r, ms));

async function typeIntoReactInput(el, text) {
  await el.evaluate((node, value) => {
    const nativeSetter = Object.getOwnPropertyDescriptor(
      window.HTMLTextAreaElement.prototype, 'value'
    ).set;
    nativeSetter.call(node, value);
    node.dispatchEvent(new Event('input', { bubbles: true }));
  }, text);
}

(async () => {
  const prompt = process.argv.slice(2).join(' ') || 'Test diagnostic';
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    userDataDir: './browser-data',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu'],
  });

  const page = await browser.newPage();
  try {
    await page.goto(DEEPSEEK_BASE, { waitUntil: 'networkidle2', timeout: 30000 });
    await wait(2000);
    if (page.url().includes('/sign_in')) {
      console.log('❌ Not authenticated.');
      return;
    }
    await page.waitForSelector(INPUT_SEL, { timeout: 10000 });
    console.log('✅ Authenticated.');

    // Inject the observer AND a listener that logs mutations
    await page.evaluate(() => {
      window.__deepseekReply = null;
      window.__deepseekDone = false;

      const targetNode = document.body;
      const config = { childList: true, subtree: true, characterData: true };

      const observer = new MutationObserver((mutations) => {
        const msgs = document.querySelectorAll('div.ds-message[data-role="assistant"] .ds-markdown');
        if (msgs.length > 0) {
          const last = msgs[msgs.length - 1];
          window.__deepseekReply = last.innerText;
          console.log('[OBSERVER] current reply length:', last.innerText.length);
        }
        const stopBtn = document.querySelector('button[aria-label="Stop generating"], button[aria-label="Stop"]');
        if (!stopBtn && window.__deepseekReply && window.__deepseekReply.trim().length > 0) {
          console.log('[OBSERVER] Done – stop button gone and reply exists.');
          window.__deepseekDone = true;
          observer.disconnect();
        }
      });

      observer.observe(targetNode, config);
      window.__observer = observer;
    });

    // Type and send
    const input = await page.$(INPUT_SEL);
    await input.click();
    await typeIntoReactInput(input, prompt);

    await page.waitForFunction(
      (sel) => {
        const btn = document.querySelector(sel);
        return btn && btn.getAttribute('aria-disabled') !== 'true';
      },
      { timeout: 10000 },
      SEND_BTN_SEL
    );
    console.log('📤 Send button enabled, clicking...');
    const sendBtn = await page.$(SEND_BTN_SEL);
    await sendBtn.click();

    // Wait up to 60 seconds for observer to set done, polling console logs
    const start = Date.now();
    while (Date.now() - start < 60000) {
      const done = await page.evaluate(() => window.__deepseekDone);
      if (done) break;
      // Dump any console logs from the page
      await wait(1000);
    }

    // Capture reply
    const reply = await page.evaluate(() => window.__deepseekReply);
    console.log('📝 Captured reply:', reply ? reply.substring(0, 200) : '(empty)');

    // Save screenshot
    await page.screenshot({ path: 'diag-screenshot.png' });
    console.log('📸 Screenshot saved to diag-screenshot.png');

    // Listen for page console messages (any missed logs)
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    await wait(2000);

  } catch (e) {
    console.error(e);
  } finally {
    await browser.close();
  }
})();
