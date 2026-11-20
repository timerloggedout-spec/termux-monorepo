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

async function main() {
  const prompt = process.argv.slice(2).join(' ') || 'Hello';
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    userDataDir: './browser-data',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu'],
  });
  const page = await browser.newPage();
  await page.goto(DEEPSEEK_BASE, { waitUntil: 'networkidle2', timeout: 30000 });
  await wait(2000);
  if (page.url().includes('/sign_in')) { console.log('❌ Auth failed'); return; }
  await page.waitForSelector(INPUT_SEL, { timeout: 10000 });
  // Expert
  const expert = await page.$('div[data-model-type="expert"][role="radio"]');
  if (expert) {
    const c = await page.evaluate(el => el.getAttribute('aria-checked'), expert);
    if (c !== 'true') { await expert.click(); await wait(500); }
  }
  const input = await page.$(INPUT_SEL);
  await input.click();
  await typeIntoReactInput(input, prompt);
  await page.waitForFunction(sel => {
    const btn = document.querySelector(sel);
    return btn && btn.getAttribute('aria-disabled') !== 'true';
  }, { timeout: 10000 }, SEND_BTN_SEL);
  const send = await page.$(SEND_BTN_SEL);
  await send.click();
  // Wait for assistant message to appear (up to 2 minutes)
  await page.waitForSelector('div.ds-message[data-role="assistant"]', { timeout: 120000 });
  // Wait until text stabilises (no change for 3 seconds)
  let last = '';
  while (true) {
    await wait(3000);
    const current = await page.$eval('div.ds-message[data-role="assistant"]:last-child .ds-markdown', el => el.innerText);
    if (current === last) break;
    last = current;
  }
  console.log(last);
  const url = new URL(page.url());
  const id = url.pathname.split('/').pop();
  if (id && id.length > 10) console.log(`🔗 Session ID: ${id}`);
  await browser.close();
}
main().catch(console.error);
