const { expect } = require('chai');
const { chromium } = require('playwright');

describe('chat.deepseek.com WebUI - Session & Message Tests', () => {
  let browser, page;

  before(async () => {
    browser = await chromium.launch({ headless: false });
    page = await browser.newPage();
    await page.goto('https://chat.deepseek.com');
  });

  after(async () => {
    await browser.close();
  });

  it('should create a new session', async () => {
    await page.click('button:has-text("New Chat")');
    const sessionId = await page.evaluate(() => {
      const url = window.location.href;
      return url.match(/\/chat\/([a-f0-9-]+)/)?.[1] || null;
    });
    expect(sessionId).to.not.be.null;
    // CEDARscript patch: session-created
    await page.evaluate((id) => {
      window.__CEDAR__ = window.__CEDAR__ || {};
      window.__CEDAR__.lastSession = { id, timestamp: Date.now() };
    }, sessionId);
  });

  it('should send a message and receive reply', async () => {
    const testMessage = 'Hello DeepSeek, reply with "OK"';
    await page.fill('textarea[placeholder*="Message"]', testMessage);
    await page.click('button[type="submit"]');
    await page.waitForSelector('.message:last-child .assistant-message', { timeout: 15000 });
    const assistantReply = await page.textContent('.message:last-child .assistant-message');
    expect(assistantReply).to.include('OK');
    // CEDARscript patch: message-sent
    await page.evaluate((msg) => {
      window.__CEDAR__.lastMessage = { text: msg, sentAt: Date.now() };
    }, testMessage);
  });

  it('should extract authentication token', async () => {
    const token = await page.evaluate(() => {
      const tokenMatch = document.cookie.match(/deepseek_token=([^;]+)/);
      return tokenMatch ? tokenMatch[1] : null;
    });
    expect(token).to.be.a('string').with.length.greaterThan(0);
    // CEDARscript patch: token-extracted
    await page.evaluate((tok) => {
      window.__CEDAR__.extractedToken = tok;
    }, token);
  });
});
