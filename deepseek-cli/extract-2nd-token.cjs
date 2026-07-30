const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch({
    headless: false,
    executablePath: '/data/data/com.termux/files/usr/bin/chromium-browser',
    userDataDir: './browser-data-account2',  // separate profile
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu']
  });
  
  const page = await browser.newPage();
  
  // Capture token from API requests
  let token = null;
  page.on('request', req => {
    const auth = req.headers()['authorization'];
    if (auth && auth.startsWith('Bearer ') && !token) {
      token = auth.replace('Bearer ', '');
      console.log('TOKEN CAPTURED:', token.substring(0,20) + '...');
      fs.writeFileSync('./token-account2.txt', token);
    }
  });
  
  console.log('Opening DeepSeek. Please log in with your 2nd account.');
  console.log('The token will be captured automatically when you send a message.');
  await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 60000 });
  
  // Wait for manual login and message send (up to 2 minutes)
  console.log('Waiting for you to log in and send a message (120s timeout)...');
  await new Promise(r => setTimeout(r, 120000));
  
  if (token) {
    console.log('\nToken saved to token-account2.txt');
  } else {
    console.log('\nNo token captured. Did you send a message?');
  }
  
  await browser.close();
})();
