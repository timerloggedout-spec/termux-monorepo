const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';
const DEEPSEEK_BASE = 'https://chat.deepseek.com/';
const INPUT_SEL = 'textarea[placeholder="Message DeepSeek"]';
const EXPERT_RADIO_SEL = 'div[data-model-type="expert"][role="radio"]';
const SEND_BTN_SEL = '._52c986b';
const PAPERCLIP_SEL = '.f02f0e25';
const RETRY_BTN_SEL = 'div.ds-icon-button svg rect[id="重新生成"]';
const HISTORY_FILE = path.join(__dirname, 'chat-history.json');

const wait = ms => new Promise(r => setTimeout(r, ms));

let browser, page;
let systemPrompt = null;
let chatLog = {};

// ---------- Helpers ----------
async function typeIntoReactInput(el, text) {
  await el.evaluate((node, value) => {
    const nativeSetter = Object.getOwnPropertyDescriptor(
      window.HTMLTextAreaElement.prototype, 'value'
    ).set;
    nativeSetter.call(node, value);
    node.dispatchEvent(new Event('input', { bubbles: true }));
    node.dispatchEvent(new Event('change', { bubbles: true }));
  }, text);
}

function loadChatHistory() {
  if (fs.existsSync(HISTORY_FILE)) {
    try { chatLog = JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8')); } catch {}
  }
}
function saveChatHistory() {
  fs.writeFileSync(HISTORY_FILE, JSON.stringify(chatLog, null, 2));
}

async function resetReplyState() {
  await page.evaluate(() => {
    window.__deepseekReplyReady = false;
    window.__deepseekAssistantReply = '';
  });
}

async function setupRequestInterception() {
  await page.evaluate((sp) => {
    window.__deepseekSystemPrompt = sp;
    const origFetch = window.fetch;
    window.fetch = async function(...args) {
      const [url, options] = args;
      if (typeof url === 'string' && url.includes('/api/v0/chat/completion')) {
        if (window.__deepseekSystemPrompt && options && options.body) {
          try {
            let body = JSON.parse(options.body);
            if (Array.isArray(body.messages)) {
              if (!body.messages.some(m => m.role === 'system')) {
                body.messages.unshift({ role: 'system', content: window.__deepseekSystemPrompt });
              }
            } else if (typeof body.prompt === 'string') {
              body.prompt = window.__deepseekSystemPrompt + '\n' + body.prompt;
            }
            options.body = JSON.stringify(body);
          } catch {}
        }
        const response = await origFetch(url, options);
        response.clone().text().then(text => {
          let assistantText = '';
          for (const line of text.split('\n')) {
            if (line.startsWith('data:')) {
              try {
                const data = JSON.parse(line.slice(5).trim());
                if (data.o === 'replace' && data.v) assistantText = data.v;
                else if (data.o === 'append' && data.v) assistantText += data.v;
              } catch {}
            }
          }
          if (assistantText) {
            window.__deepseekAssistantReply = assistantText;
            window.__deepseekReplyReady = true;
          }
        }).catch(() => {});
        return response;
      }
      return origFetch(...args);
    };
  }, systemPrompt);
}

async function handleAutoRetry(attempts = 3, cooldown = 15000) {
  for (let i = 0; i < attempts; i++) {
    const reply = await page.evaluate(() => window.__deepseekAssistantReply || '');
    if (!/server is busy|thought for 0 seconds/i.test(reply)) return reply;
    console.log(`⚠️ Server busy. Retrying in ${cooldown/1000}s...`);
    await wait(cooldown);
    const retryBtn = await page.$(RETRY_BTN_SEL);
    if (!retryBtn) return reply;
    await resetReplyState();
    await retryBtn.click();
    try {
      await page.waitForFunction(() => window.__deepseekReplyReady, { timeout: 120000 });
    } catch {}
  }
  return await page.evaluate(() => window.__deepseekAssistantReply || '');
}

// ---------- Robust file upload (waits for API response) ----------
async function uploadFile(filePath) {
  const absPath = path.resolve(filePath);
  if (!fs.existsSync(absPath)) {
    console.log(`❌ Attachment not found: ${absPath}`);
    return false;
  }
  const baseName = path.basename(absPath);

  // Click paperclip and wait for file chooser
  const paperclip = await page.$(PAPERCLIP_SEL);
  if (!paperclip) {
    console.log('❌ Paperclip button not found.');
    return false;
  }

  // Set up a response promise for the upload
  let uploadResolve;
  const uploadPromise = new Promise(res => { uploadResolve = res; });
  const onResponse = async (resp) => {
    if (resp.url().includes('/api/v0/file/upload_file') && resp.request().method() === 'POST') {
      try {
        const body = await resp.text();
        uploadResolve({ status: resp.status(), body });
      } catch {
        uploadResolve({ status: resp.status(), body: '' });
      }
      page.off('response', onResponse);
    }
  };
  page.on('response', onResponse);

  // Timeout after 15s
  const timeout = setTimeout(() => {
    uploadResolve(null);
    page.off('response', onResponse);
  }, 15000);

  try {
    const [fileChooser] = await Promise.all([
      page.waitForFileChooser({ timeout: 10000 }),
      paperclip.click()
    ]);
    await fileChooser.accept([absPath]);
    console.log(`📎 File selected: ${baseName}. Waiting for upload...`);
  } catch (e) {
    console.log(`❌ File chooser failed: ${e.message}`);
    page.off('response', onResponse);
    clearTimeout(timeout);
    return false;
  }

  const result = await uploadPromise;
  clearTimeout(timeout);

  if (result && result.status === 200) {
    console.log('✅ File uploaded successfully.');
    // Optionally extract file ID
    try {
      const json = JSON.parse(result.body);
      const fileId = json?.data?.biz_data?.id;
      if (fileId) console.log(`   File ID: ${fileId}`);
    } catch {}
    return true;
  } else {
    console.log('⚠️ Upload did not complete.');
    return false;
  }
}

// ---------- Send message ----------
async function sendMessage(prompt, edit = false, fileToAttach = null) {
  await resetReplyState();

  if (fileToAttach) {
    const success = await uploadFile(fileToAttach);
    if (!success) console.log('⚠️ Continuing without file attachment.');
    await wait(500);
  }

  let targetTextarea = null;
  if (edit) {
    const userMsgs = await page.$$('div.ds-message[data-role="user"]');
    if (userMsgs.length > 0) {
      const lastMsg = userMsgs[userMsgs.length - 1];
      const pencil = await lastMsg.$('.d4910adc');
      if (pencil) {
        await pencil.click();
        await wait(600);
        const editArea = await lastMsg.$('textarea');
        if (editArea) targetTextarea = editArea;
      }
    }
  }
  if (!targetTextarea) targetTextarea = await page.$(INPUT_SEL);
  if (!targetTextarea) throw new Error('Could not find the message textarea.');

  await targetTextarea.click();
  await typeIntoReactInput(targetTextarea, prompt);

  await page.waitForFunction(
    (sel) => {
      const btn = document.querySelector(sel);
      return btn && btn.getAttribute('aria-disabled') !== 'true';
    },
    { timeout: 10000 },
    SEND_BTN_SEL
  );
  const sendBtn = await page.$(SEND_BTN_SEL);
  if (!sendBtn) throw new Error('Send button not found.');
  await sendBtn.click();
  console.log('📤 Message sent.');

  // Capture new session ID if URL changes
  try {
    await page.waitForFunction((oldUrl) => window.location.href !== oldUrl, { timeout: 5000 }, page.url());
  } catch {}

  try {
    await page.waitForFunction(() => window.__deepseekReplyReady, { timeout: 120000 });
  } catch {
    return '';
  }
  let reply = await page.evaluate(() => window.__deepseekAssistantReply || '');
  reply = await handleAutoRetry() || reply;
  return reply;
}

// ---------- Init session ----------
async function initSession(sessionId = null) {
  browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROMIUM_PATH,
    userDataDir: './browser-data',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu'],
  });
  page = await browser.newPage();
  const targetUrl = sessionId ? `${DEEPSEEK_BASE}a/chat/s/${sessionId}` : DEEPSEEK_BASE;
  await page.goto(targetUrl, { waitUntil: 'networkidle2', timeout: 30000 });
  await wait(2000);
  if (page.url().includes('/sign_in')) {
    console.error('❌ Not authenticated. Run manual login again.');
    await browser.close();
    process.exit(1);
  }
  await page.waitForSelector(INPUT_SEL, { timeout: 10000 });
  console.log('✅ Authenticated.');

  const expertRadio = await page.$(EXPERT_RADIO_SEL);
  if (expertRadio) {
    const checked = await page.evaluate(el => el.getAttribute('aria-checked'), expertRadio);
    if (checked !== 'true') {
      await expertRadio.click();
      await wait(800);
    }
  }
  await setupRequestInterception();
}

// ---------- CLI ----------
async function main() {
  const args = process.argv.slice(2);
  let sessionId = null, editMode = false, loopMode = false, listMode = false, showLog = false;
  let systemPromptFile = null, attachFile = null;
  let prompt = '';
  let promptIndex = args.findIndex(a => !a.startsWith('--'));
  if (promptIndex > -1) { prompt = args.slice(promptIndex).join(' '); args.splice(promptIndex); }

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--session' && args[i+1]) { sessionId = args[i+1]; i++; }
    else if (args[i] === '--edit') editMode = true;
    else if (args[i] === '--loop') loopMode = true;
    else if (args[i] === '--list') listMode = true;
    else if (args[i] === '--log') showLog = true;
    else if (args[i] === '--system-prompt' && args[i+1]) { systemPrompt = args[i+1]; i++; }
    else if (args[i] === '--system-prompt-file' && args[i+1]) { try { systemPrompt = fs.readFileSync(args[i+1], 'utf8').trim(); } catch {} i++; }
    else if (args[i] === '--attach' && args[i+1]) { attachFile = args[i+1]; i++; }
  }

  loadChatHistory();
  if (showLog) { console.log(JSON.stringify(chatLog, null, 2)); return; }

  if (listMode) {
    await initSession();
    const sessions = await page.evaluate(() => {
      const items = document.querySelectorAll('._546d736, .ds-conversation-item');
      return Array.from(items).map((item, idx) => {
        const titleEl = item.querySelector('.c08e6e93, .ds-conversation-title');
        return { index: idx, title: titleEl ? titleEl.innerText.trim() : '(no title)' };
      });
    });
    console.log('📋 Recent chat sessions:');
    sessions.forEach(s => console.log(`  [${s.index}] ${s.title}`));
    console.log('\n📁 Local history sessions:');
    Object.keys(chatLog).forEach(id => console.log(`  ${id}  "${chatLog[id].title}"`));
    await browser.close();
    return;
  }

  if (loopMode) {
    await initSession(sessionId);
    if (!sessionId) { const url = new URL(page.url()); sessionId = url.pathname.split('/').pop(); }
    if (!chatLog[sessionId]) chatLog[sessionId] = { title: await page.title(), messages: [] };
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    for await (const line of rl) {
      if (line.trim()) {
        chatLog[sessionId].messages.push({ role: 'user', content: line.trim(), edited: false, time: Date.now() });
        const reply = await sendMessage(line.trim(), editMode, attachFile);
        console.log(reply);
        chatLog[sessionId].messages.push({ role: 'assistant', content: reply, time: Date.now() });
        saveChatHistory();
        editMode = false; attachFile = null;
      }
    }
    await browser.close();
    return;
  }

  if (!prompt) { console.error('Usage: deepseek.js [--session <ID>] [--edit] [--attach <file>] ... "prompt"'); process.exit(1); }

  await initSession(sessionId);
  const reply = await sendMessage(prompt, editMode, attachFile);
  const currentUrl = new URL(page.url());
  const currentId = sessionId || currentUrl.pathname.split('/').pop() || 'unknown';
  if (!chatLog[currentId]) chatLog[currentId] = { title: await page.title(), messages: [] };
  if (editMode && chatLog[currentId].messages.length > 0) {
    const msgs = chatLog[currentId].messages;
    for (let i = msgs.length - 1; i >= 0; i--) {
      if (msgs[i].role === 'user') { msgs[i].content = prompt; msgs[i].edited = true; break; }
    }
  } else {
    chatLog[currentId].messages.push({ role: 'user', content: prompt, edited: false, time: Date.now() });
  }
  console.log(reply);
  chatLog[currentId].messages.push({ role: 'assistant', content: reply, time: Date.now() });
  saveChatHistory();
  console.log(`🔗 Session ID: ${currentId}`);
  await browser.close();
}

main().catch(err => { console.error('💥 Fatal error:', err.message); process.exit(2); });
