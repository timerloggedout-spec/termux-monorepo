import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const { execSync } = require('child_process');
const token = execSync('python3 -c "import sys; sys.path.insert(0,\'/data/data/com.termux/files/home/deepcli\'); from deepcli.core import get_token; print(get_token())"').toString().trim();

const versionSets = [
  { client: '1.3.0-auto-resume', app: '20241129.1' },
  { client: '1.4.0', app: '20250521.1' },
  { client: '1.5.0', app: '20250601.1' },
  { client: '1.6.0', app: '20250915.1' },
  { client: '2.0.0', app: '20260501.1' },
  { client: '1.3.0', app: '20250101.1' },
  { client: '1.2.0', app: '20241001.1' },
  { client: '1.0.0', app: '20240901.1' },
];

async function test(clientVer, appVer) {
  try {
    const hdrs = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'X-Client-Version': clientVer,
      'X-App-Version': appVer,
      'X-Client-Platform': 'web',
      'X-Client-Locale': 'en_US',
      'Origin': 'https://chat.deepseek.com',
      'Referer': 'https://chat.deepseek.com/',
    };
    // Create session
    const cs = await fetch('https://chat.deepseek.com/api/v0/chat_session/create', {
      method: 'POST', headers: hdrs,
      body: JSON.stringify({ character_id: null, model_type: 'expert' })
    });
    const sdata = await cs.json();
    const sid = sdata?.data?.biz_data?.id;
    if (!sid) return { clientVer, appVer, result: 'NO_SESSION' };
    // Send probe
    const res = await fetch('https://chat.deepseek.com/api/v0/chat/completion', {
      method: 'POST', headers: { ...hdrs, 'Accept': 'text/event-stream' },
      body: JSON.stringify({ chat_session_id: sid, prompt: 'Say "expert unlocked"', stream: true, model_type: 'expert' })
    });
    const reader = res.body.getReader();
    let text = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = new TextDecoder().decode(value);
      for (const line of chunk.split('\n')) {
        if (line.startsWith('data:')) {
          try {
            const d = JSON.parse(line.slice(5).trim());
            if (d.v) text += d.v;
          } catch(e) {}
        }
      }
    }
    const success = text.toLowerCase().includes('expert') && !text.includes('Update to the latest');
    return { clientVer, appVer, result: success ? 'EXPERT_OK' : 'BLOCKED', snippet: text.slice(0, 100) };
  } catch(e) {
    return { clientVer, appVer, result: 'ERROR: ' + e.message };
  }
}

const results = [];
for (const vs of versionSets) {
  const r = await test(vs.client, vs.app);
  console.log(JSON.stringify(r));
  results.push(r);
}
const winners = results.filter(r => r.result === 'EXPERT_OK');
console.log(`\nWinners: ${winners.length}/${results.length}`);
if (winners.length > 0) {
  console.log('Working version:', JSON.stringify(winners[0]));
}
