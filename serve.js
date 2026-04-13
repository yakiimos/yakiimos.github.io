const http = require('http');
const fs = require('fs');
const path = require('path');

const port = 4321;
const root = process.cwd();

const types = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
};

http.createServer((req, res) => {
  let urlPath = req.url.split('?')[0];
  if (urlPath === '/') urlPath = '/index.html';
  
  let filePath = path.join(root, urlPath);
  
  if (!fs.existsSync(filePath)) {
    filePath = filePath + '/index.html';
  }
  
  if (!fs.existsSync(filePath)) {
    res.writeHead(404);
    res.end('Not Found');
    return;
  }
  
  const ext = path.extname(filePath);
  res.writeHead(200, { 'Content-Type': types[ext] || 'text/plain' });
  res.end(fs.readFileSync(filePath));
}).listen(port, () => {
  console.log('Server running at http://localhost:' + port);
});
