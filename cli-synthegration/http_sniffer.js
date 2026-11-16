const http = require('http');
const fs = require('fs');
const PORT = process.argv[2] || 8888;
const LOG = process.argv[3] || (__dirname + '/sniffer_capture.log');

function log(msg) {
    console.log(msg);
    fs.appendFileSync(LOG, msg + '\n');
}

const server = http.createServer((req, res) => {
    let body = [];
    req.on('data', chunk => body.push(chunk));
    req.on('end', () => {
        const fullBody = Buffer.concat(body).toString();
        log(`\n=== ${req.method} ${req.url} ===`);
        for (const [k,v] of Object.entries(req.headers)) {
            if (k.includes('client') || k.includes('app') || k.includes('version') ||
                k.includes('auth') || k.includes('expert') || k.includes('content') ||
                k.includes('cookie') || k.includes('x-ds')) {
                log(`  ${k}: ${v}`);
            }
        }
        if (fullBody && fullBody.length < 5000) {
            log(`  BODY: ${fullBody.slice(0,2000)}`);
        }
        res.writeHead(200, {'Content-Type': 'text/plain'});
        res.end('OK');
    });
});

server.on('connect', (req, clientSocket, head) => {
    const [host, port] = req.url.split(':');
    log(`\n=== CONNECT ${host}:${port || 443} ===`);
    const serverSocket = require('net').connect(port || 443, host, () => {
        clientSocket.write('HTTP/1.1 200 Connection Established\r\n\r\n');
        serverSocket.write(head);
        serverSocket.pipe(clientSocket);
        clientSocket.pipe(serverSocket);
    });
    serverSocket.on('error', () => clientSocket.end());
});

server.listen(PORT, () => log(`Sniffer on :${PORT} → ${LOG}`));
