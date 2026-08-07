const http = require('http');
const fs = require('fs');
const path = require('path');
const base = path.join(__dirname, 'public');
const server = http.createServer((req, res) => {
  let pathname = req.url === '/' ? '/index.html' : req.url;
  const filePath = path.join(base, pathname);
  fs.readFile(filePath, (err, data) => {
    if (err) { res.writeHead(404); res.end('Not found'); return; }
    res.writeHead(200); res.end(data);
  });
});
const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';
server.listen(PORT, HOST, () => console.log(`PWA served at http://${HOST}:${PORT}`));
