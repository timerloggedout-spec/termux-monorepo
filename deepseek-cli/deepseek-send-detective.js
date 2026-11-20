const puppeteer = require('puppeteer');
const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const DEEPSEEK_BASE = 'https://chat.deepseek.com/';
const INPUT_SEL = 'textarea[placeholder="Message DeepSeek"]';
const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const session = process.env.SESSION_ID || '';
  const prompt = process.argv.slice(2).join(' ') || 'Test PING';

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    userDataDir: './browser-data',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu'],
  });

  const page = await browser.newPage();
  try {
    const targetUrl = session ? `${DEEPSEEK_BASE}a/chat/s/${session}` : DEEPSEEK_BASE;
    await page.goto(targetUrl, { waitUntil: 'networkidle2', timeout: 30000 });
    await wait(2000);
    if (page.url().includes('/sign_in')) { console.log('❌ Auth failed.'); return; }

    await page.waitForSelector(INPUT_SEL, { timeout: 10000 });
    console.log('✅ Input found.');

    // Ensure Expert mode
    const expert = await page.$('div[data-model-type="expert"][role="radio"]');
    if (expert) {
      const checked = await page.evaluate(el => el.getAttribute('aria-checked'), expert);
      if (checked !== 'true') { await expert.click(); await wait(500); }
    }

    const input = await page.$(INPUT_SEL);
    await input.click();
    await page.type(INPUT_SEL, prompt, { delay: 20 });
    console.log(`⌨️ Typed: "${prompt}"`);

    // -------------------------------------------------------------
    // HUNT FOR THE SEND BUTTON (many possible selectors)
    // -------------------------------------------------------------
    const sendSelectors = [
      'button[aria-label="Send"]',
      'button[aria-label="Send message"]',
      'button[type="submit"]',
      'svg[data-icon="send"]',
      'div[role="button"][aria-label="Send"]',
      'button._send-btn',               // hypothetical
      'button:has(svg[data-icon="send"])',
      'textarea + button',              // adjacent sibling
    ];

    let sendBtn = null;
    for (const sel of sendSelectors) {
      try {
        const el = await page.$(sel);
        if (el) {
          sendBtn = el;
          console.log(`🔘 Found send button with selector: ${sel}`);
          break;
        }
      } catch {}
    }

    if (!sendBtn) {
      // Fallback: search for any button that appears after text is entered
      console.log('🔍 No explicit button found; trying to locate any nearby button...');
      const nearbyButtons = await page.evaluate((inputSel) => {
        const input = document.querySelector(inputSel);
        if (!input) return [];
        const form = input.closest('form') || input.parentElement;
        const buttons = Array.from(form.querySelectorAll('button, [role="button"]'));
        return buttons.map(b => ({
          ariaLabel: b.getAttribute('aria-label'),
          text: b.innerText?.substring(0, 30),
          class: b.className,
          outerHTML: b.outerHTML.substring(0, 150),
        }));
      }, INPUT_SEL);
      console.log('📦 Nearby buttons:', JSON.stringify(nearbyButtons, null, 2));
      // Try the first button that looks like a send
      const maybeSend = nearbyButtons.find(b => 
        (b.ariaLabel && /send/i.test(b.ariaLabel)) ||
        (b.text && /send/i.test(b.text)) ||
        /_send/i.test(b.class)
      );
      if (maybeSend) {
        sendBtn = await page.$(`button[aria-label="${maybeSend.ariaLabel}"]`) || 
                  await page.$(`[role="button"][aria-label="${maybeSend.ariaLabel}"]`);
      }
    }

    if (sendBtn) {
      console.log('📤 Clicking send button...');
      await sendBtn.click();
    } else {
      console.log('📤 No send button found; pressing Enter with delay...');
      await page.keyboard.press('Enter');
      await wait(500);
    }

    await wait(1000);

    // Check if message appeared
    const msgCount = await page.$$eval('div.ds-message[data-role="assistant"]', els => els.length);
    console.log('💬 Assistant messages now:', msgCount);

    // Save screenshot
    await page.screenshot({ path: 'detective-send.png' });
    console.log('📸 Screenshot saved to detective-send.png');

  } catch (e) {
    console.error(e);
  } finally {
    await browser.close();
  }
})();
