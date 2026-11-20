import puppeteer from 'puppeteer';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const USER_DATA_DIR = process.argv[2] || path.join(__dirname, 'browser-data');

const CHROMIUM_PATH = '/data/data/com.termux/files/usr/bin/chromium-browser';

async function getToken() {
    const browser = await puppeteer.launch({
        headless: 'new',
        executablePath: CHROMIUM_PATH,
        userDataDir: USER_DATA_DIR,
        args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu']
    });
    const page = await browser.newPage();

    let token = null;

    // Intercept all requests and grab the Authorization header from any API call
    page.on('request', req => {
        const url = req.url();
        if (url.includes('/api/v0/')) {
            const authHeader = req.headers()['authorization'];
            if (authHeader && authHeader.startsWith('Bearer ')) {
                token = authHeader.replace('Bearer ', '');
            }
        }
    });

    // Navigate to the main page and trigger an API call
    await page.goto('https://chat.deepseek.com/', { waitUntil: 'networkidle2', timeout: 30000 });

    // If token not captured yet, manually fetch a protected endpoint to force an auth header
    if (!token) {
        try {
            await page.evaluate(async () => {
                await fetch('/api/v0/chat_session/fetch_page');
            });
            // Wait a moment for the request to fire
            await page.waitForTimeout(2000);
        } catch (e) {}
    }

    if (!token) {
        // Last resort: try localStorage
        token = await page.evaluate(() => localStorage.getItem('userToken'));
    }

    if (!token) {
        console.error('No token found via network interception or localStorage.');
        process.exit(1);
    }

    console.log(token);
    await browser.close();
}

getToken().catch(e => { console.error(e.message); process.exit(2); });
