const puppeteer = require('puppeteer');
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const DEEPSEEK_BASE = 'https://chat.deepseek.com/';
const INPUT_SEL = 'textarea[placeholder="Message DeepSeek"]';
const EXPERT_RADIO_SEL = 'div[data-model-type="expert"][role="radio"]';
const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const prompt = process.argv.slice(2).join(' ').trim() || 'Debug test prompt';
  const session = process.env.SESSION_ID || '';

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    userDataDir: './browser-data',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu'],
  });

  const page = await browser.newPage();
  try {
    const targetUrl = session ? `${DEEPSEEK_BASE}a/chat/s/${session}` : DEEPSEEK_BASE;
    console.log(`📍 Going to: ${targetUrl}`);
    await page.goto(targetUrl, { waitUntil: 'networkidle2', timeout: 30000 });
    await wait(2000);

    if (page.url().includes('/sign_in')) {
      console.log('❌ Not authenticated.');
      process.exit(1);
    }

    await page.waitForSelector(INPUT_SEL, { timeout: 10000 });
    console.log('✅ Input found.');

    // Expert mode
    const expert = await page.$(EXPERT_RADIO_SEL);
    if (expert) {
      const checked = await page.evaluate(el => el.getAttribute('aria-checked'), expert);
      if (checked !== 'true') {
        await expert.click();
        await wait(500);
      }
    }

    // Type prompt
    const input = await page.$(INPUT_SEL);
    await input.click();
    await page.type(INPUT_SEL, prompt, { delay: 20 });
    console.log(`⌨️  Typed: "${prompt}"`);

    // Look for a send button (common aria-labels: "Send message", "Submit", or a paper plane icon)
    const sendBtn = await page.$('button[aria-label="Send"], button[aria-label="Send message"], button[type="submit"], svg[data-icon="send"]');
    if (sendBtn) {
      console.log('📤 Clicking send button:', await page.evaluate(el => el.outerHTML.substring(0,100), sendBtn));
      await sendBtn.click();
    } else {
      console.log('📤 No explicit send button found; pressing Enter.');
      await page.keyboard.press('Enter');
    }
    await wait(1000);

    // Take screenshot
    await page.screenshot({ path: 'debug-send.png' });
    console.log('📸 Screenshot saved to debug-send.png');

    // Check if input is cleared (indicates message was sent)
    const inputValue = await page.evaluate((sel) => document.querySelector(sel)?.value || '', INPUT_SEL);
    console.log('📝 Input field value after send:', inputValue ? `"${inputValue.substring(0,50)}"` : '(empty)');

    // Count assistant messages
    const msgCount = await page.$$eval('div.ds-message[data-role="assistant"]', els => els.length);
    console.log('💬 Assistant messages in DOM:', msgCount);
  } catch (e) {
    console.error(e);
  } finally {
    await browser.close();
  }
})();
