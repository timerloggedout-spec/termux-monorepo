const puppeteer = require('puppeteer');
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const DEEPSEEK_BASE = 'https://chat.deepseek.com/';
const INPUT_SEL = 'textarea[placeholder="Message DeepSeek"]';
const SEND_BTN_SEL = '._52c986b';
const wait = ms => new Promise(r => setTimeout(r, ms));

async function typeIntoReactInput(el, text) {
  await el.evaluate((node, value) => {
    const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
    setter.call(node, value);
    node.dispatchEvent(new Event('input', { bubbles: true }));
  }, text);
}

(async () => {
  const prompt = process.argv.slice(2).join(' ') || 'Hello';
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
    if (page.url().includes('/sign_in')) { console.log('❌ Auth failed'); return; }
    await page.waitForSelector(INPUT_SEL, { timeout: 10000 });

    // Expert mode
    const expert = await page.$('div[data-model-type="expert"][role="radio"]');
    if (expert) {
      const c = await page.evaluate(el => el.getAttribute('aria-checked'), expert);
      if (c !== 'true') { await expert.click(); await wait(500); }
    }

    // Send
    const input = await page.$(INPUT_SEL);
    await input.click();
    await typeIntoReactInput(input, prompt);
    await page.waitForFunction(sel => {
      const btn = document.querySelector(sel);
      return btn && btn.getAttribute('aria-disabled') !== 'true';
    }, { timeout: 10000 }, SEND_BTN_SEL);
    const sendBtn = await page.$(SEND_BTN_SEL);
    await sendBtn.click();

    // Wait for possible reply / continue button
    console.log('⏳ Waiting 20 seconds for generation...');
    await wait(20000);

    // Dump all possible assistant message elements
    const assistantCandidates = await page.evaluate(() => {
      const selectors = [
        'div.ds-message[data-role="assistant"]',
        '.ds-markdown',
        '[class*="ds-markdown"]',
        '.ds-assistant-message',
        '[data-role="assistant"]',
        '.ds-virtual-list-visible-items > div:last-child',
      ];
      const results = [];
      for (const sel of selectors) {
        const els = document.querySelectorAll(sel);
        els.forEach((el, i) => {
          results.push({
            selector: sel,
            index: i,
            text: el.innerText?.substring(0, 200),
            classes: el.className,
          });
        });
      }
      return results;
    });
    console.log('📋 Assistant candidate elements:');
    assistantCandidates.forEach(r => console.log(JSON.stringify(r)));

    // Look for continue button
    const continueBtn = await page.evaluate(() => {
      const btns = document.querySelectorAll('button, [role="button"]');
      for (const btn of btns) {
        const text = btn.innerText?.trim().toLowerCase();
        const cls = btn.className.toLowerCase();
        if (text.includes('continue') || cls.includes('secondary')) {
          return { text: btn.innerText, classes: btn.className };
        }
      }
      return null;
    });
    console.log('🔘 Continue button found:', JSON.stringify(continueBtn));

    // Screenshot
    await page.screenshot({ path: 'inspect-page.png' });
    console.log('📸 inspect-page.png saved');
  } catch (e) {
    console.error(e);
  } finally {
    await browser.close();
  }
})();
