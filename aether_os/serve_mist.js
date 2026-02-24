const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3333;
const DIR = __dirname;

const MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'text/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml'
};

const server = http.createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/api/task') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', async () => {
            try {
                const newTask = JSON.parse(body);
                const tasksPath = path.join(DIR, '..', 'workspace', 'pending-tasks.json');
                const tasks = JSON.parse(fs.readFileSync(tasksPath, 'utf8'));
                tasks.push(newTask);
                fs.writeFileSync(tasksPath, JSON.stringify(tasks, null, 2));

                const { exec } = require('child_process');
                exec('node aether_os/skills/heartbeat_check.js', { cwd: path.join(DIR, '..') }, (error, stdout, stderr) => {
                    if (error) console.error(`Heartbeat error: ${error}`);
                    if (stdout) console.log(`Heartbeat output: ${stdout}`);
                    if (stderr) console.error(`Heartbeat stderr: ${stderr}`);
                });

                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ ok: true, message: 'Task added and heartbeat triggered' }));
            } catch (err) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ ok: false, error: 'Invalid JSON or filing error' }));
            }
        });
        return;
    }

    let filePath = path.join(DIR, req.url === '/' ? 'mist_chat.html' : req.url);
    const ext = path.extname(filePath);
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    fs.readFile(filePath, (err, content) => {
        if (err) {
            res.writeHead(404);
            res.end('Not Found');
            return;
        }
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(content);
    });
});

server.listen(PORT, () => {
    console.log(`✧ MIST Chat Server running at http://localhost:${PORT}`);
    console.log('   Open this URL in your browser to connect to MIST.');
});
