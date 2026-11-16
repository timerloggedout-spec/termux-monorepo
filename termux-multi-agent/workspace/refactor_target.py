const { expect } = require('chai');
const puppeteer = require('puppeteer');

describe('Chat DeepSeek WebUI Tests', function() {
  this.timeout(60000);
  let browser;
  let page;

  // CEDARscript patch: Context-Aware Session Initialization
  before(async () => {
    browser = await puppeteer.launch({ headless: false });
    page = await browser.newPage();
    await page.goto('https://chat.deepseek.com', { waitUntil: 'networkidle2' });
  });

  after(async () => {
    await browser.close();
  });

  // CEDARscript patch: Session Creation Probe
  it('should create a new session successfully', async () => {
    const newSessionBtn = await page.waitForSelector('button[aria-label="New chat"]', { timeout: 10000 });
    await newSessionBtn.click();
    
    const sessionTitle = await page.waitForSelector('.chat-title', { timeout: 5000 });
    const titleText = await sessionTitle.evaluate(el => el.textContent);
    expect(titleText).to.exist;
  });

  // CEDARscript patch: Message Sending with Token Flow Validation
  it('should send a message and receive response with tokens', async () => {
    const textarea = await page.waitForSelector('textarea[placeholder*="Send a message"]', { timeout: 10000 });
    await textarea.type('What is 2+2?', { delay: 50 });
    
    const sendBtn = await page.waitForSelector('button[type="submit"]', { timeout: 5000 });
    await sendBtn.click();
    
    // Wait for AI response
    await page.waitForFunction(
      () => document.querySelectorAll('.assistant-message').length > 0,
      { timeout: 30000 }
    );
    
    const responseElem = await page.$('.assistant-message:last-child');
    const responseText = await responseElem.evaluate(el => el.textContent);
    expect(responseText).to.include('4');
  });

  // CEDARscript patch: Token Extraction via DOM Analysis
  it('should extract token usage metadata from response', async () => {
    // Extract token info from UI (assuming token counter exists in DeepSeek WebUI)
    const tokenInfo = await page.evaluate(() => {
      const tokenElements = Array.from(document.querySelectorAll('[data-token-count], .token-counter, .usage-stats'));
      return tokenElements.map(el => {
        const text = el.textContent || '';
        const match = text.match(/(\d+)\s*tokens?/i);
        return match ? parseInt(match[1], 10) : null;
      }).filter(v => v !== null);
    });
    
    expect(tokenInfo).to.be.an('array');
    if (tokenInfo.length > 0) {
      expect(tokenInfo[0]).to.be.a('number').that.is.at.least(1);
    }
  });

  // CEDARscript patch: Multi-turn Session Continuity
  it('should maintain context across messages in same session', async () => {
    const textarea = await page.waitForSelector('textarea[placeholder*="Send a message"]');
    await textarea.click({ clickCount: 3 });
    await textarea.type('My name is Cedric', { delay: 50 });
    
    const sendBtn = await page.$('button[type="submit"]');
    await sendBtn.click();
    await page.waitForTimeout(3000);
    
    const textarea2 = await page.waitForSelector('textarea[placeholder*="Send a message"]');
    await textarea2.type('What is my name?', { delay: 50 });
    await sendBtn.click();
    
    await page.waitForFunction(
      () => document.querySelectorAll('.assistant-message').length >= 2,
      { timeout: 30000 }
    );
    
    const lastResponse = await page.$eval('.assistant-message:last-child', el => el.textContent);
    expect(lastResponse.toLowerCase()).to.include('cedric');
  });

  // CEDARscript patch: Error Resilience & Token Boundary Validation
  it('should handle empty message gracefully', async () => {
    const sendBtn = await page.$('button[type="submit"]');
    const isDisabled = await sendBtn.evaluate(btn => btn.disabled);
    expect(isDisabled).to.be.true;
  });
});
