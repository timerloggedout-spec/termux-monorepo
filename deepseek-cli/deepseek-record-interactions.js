const puppeteer = require('puppeteer');
const fs = require('fs');
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const DEEPSEEK_BASE = 'https://chat.deepseek.com/';
const INPUT_SEL = 'textarea[placeholder="Message DeepSeek"]';
const EXPERT_RADIO_SEL = 'div[data-model-type="expert"][role="radio"]';
const USER_MSG_SEL = 'div.ds-message[data-role="user"]';
const EDIT_PENCIL_SEL = '.d4910adc';
const SEND_BTN_SEL = '._52c986b';
const wait = ms => new Promise(r => setTimeout(r, ms));

async function typeIntoReactInput(el, text) {
  await el.evaluate((node, value) => {
    const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
    setter.call(node, value);
    node.dispatchEvent(new Event('input', { bubbles: true }));
    node.dispatchEvent(new Event('change', { bubbles: true }));
  }, text);
}

(async () => {
  const sessionId = process.argv[2];
  if (!sessionId) {
    console.error('Usage: node deepseek-record-interactions.js <session-id>');
    process.exit(1);
  }

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    userDataDir: './browser-data',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu'],
  });
  const page = await browser.newPage();

  // Log all console messages from the page
  page.on('console', msg => console.log('PAGE:', msg.text()));

  // Inject a global click logger and DOM observer
  await page.evaluateOnNewDocument(() => {
    document.addEventListener('click', e => {
      const el = e.target.closest('button, [role="button"], a');
      if (el) {
        console.log('[CLICK]', el.innerText?.trim()?.substring(0,50), '| classes:', el.className, '| aria:', el.getAttribute('aria-label'));
      }
    }, true);
    const observer = new MutationObserver(mutations => {
      for (const m of mutations) {
        for (const node of m.addedNodes) {
          if (node.nodeType === 1 && node.matches('button, [role="button"], .ds-modal, .ds-popover')) {
            console.log('[DOM ADDED]', node.innerText?.trim()?.substring(0,50), '| classes:', node.className);
          }
        }
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  });

  try {
    // 1. Go to session
    const targetUrl = `${DEEPSEEK_BASE}a/chat/s/${sessionId}`;
    console.log(`Navigating to ${targetUrl}`);
    await page.goto(targetUrl, { waitUntil: 'networkidle2', timeout: 30000 });
    await wait(2000);
    if (page.url().includes('/sign_in')) { console.log('❌ Auth failed'); return; }
    console.log('✅ Authenticated.');

    // Expert mode
    const expert = await page.$(EXPERT_RADIO_SEL);
    if (expert) {
      const checked = await page.evaluate(el => el.getAttribute('aria-checked'), expert);
      if (checked !== 'true') { await expert.click(); await wait(800); }
    }

    // 2. Find last user message and click edit pencil
    const userMsgs = await page.$$(USER_MSG_SEL);
    if (userMsgs.length === 0) {
      console.log('❌ No user messages in this session.');
      await browser.close();
      return;
    }
    const lastMsg = userMsgs[userMsgs.length - 1];
    const pencil = await lastMsg.$(EDIT_PENCIL_SEL);
    if (!pencil) {
      console.log('❌ Edit pencil not found on last message.');
      await browser.close();
      return;
    }
    console.log('Clicking edit pencil...');
    await pencil.click();
    await wait(1000);

    // 3. Dump all buttons visible after edit mode
    const buttons = await page.evaluate(() => {
      const btns = document.querySelectorAll('button, [role="button"]');
      return Array.from(btns).map(b => ({
        text: b.innerText?.trim().substring(0,100),
        classes: b.className,
        aria: b.getAttribute('aria-label'),
        disabled: b.getAttribute('aria-disabled'),
        visible: b.offsetParent !== null,
      }));
    });
    console.log('\n📋 All buttons after edit mode:');
    buttons.filter(b => b.visible).forEach(b => console.log(JSON.stringify(b)));

    // 4. Save screenshot and full DOM
    await page.screenshot({ path: 'edit-mode.png', fullPage: true });
    fs.writeFileSync('edit-mode.html', await page.content());
    console.log('📸 Screenshot: edit-mode.png | DOM: edit-mode.html');

    // 5. Type a new prompt and look for update/fork buttons
    const editArea = await lastMsg.$('textarea');
    if (editArea) {
      await typeIntoReactInput(editArea, 'Test edit to discover fork controls');
      await wait(800);
      const postEditButtons = await page.evaluate(() => {
        const btns = document.querySelectorAll('button, [role="button"]');
        return Array.from(btns).map(b => ({
          text: b.innerText?.trim().substring(0,100),
          classes: b.className,
          aria: b.getAttribute('aria-label'),
          disabled: b.getAttribute('aria-disabled'),
          visible: b.offsetParent !== null,
        }));
      });
      console.log('\n📋 Buttons after typing edit:');
      postEditButtons.filter(b => b.visible).forEach(b => console.log(JSON.stringify(b)));
      await page.screenshot({ path: 'edit-typed.png', fullPage: true });
    }

    console.log('\n✅ Done. Check edit-mode.png and edit-typed.png for visual layout.');
  } catch (e) {
    console.error(e);
  } finally {
    await browser.close();
  }
})();
