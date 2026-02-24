const express = require('express');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3333;
const DIR = __dirname;
const ROOT = path.join(DIR, '..');

// ── Middleware ──
app.use(express.json());
app.use((req, res, next) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    if (req.method === 'OPTIONS') return res.sendStatus(200);
    next();
});

// ── SSE client registry ──
const sseClients = new Set();

function broadcast(event, data) {
    const payload = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
    for (const res of sseClients) {
        try { res.write(payload); } catch (e) { sseClients.delete(res); }
    }
}

// ── SSE stream endpoint ──
app.get('/api/stream', (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('X-Accel-Buffering', 'no');
    res.flushHeaders();

    // Send initial state
    res.write(`event: connected\ndata: ${JSON.stringify({ status: 'ok', ts: new Date().toISOString() })}\n\n`);

    // Send current tasks
    const tasksPath = path.join(ROOT, 'workspace', 'pending-tasks.json');
    if (fs.existsSync(tasksPath)) {
        try {
            const tasks = JSON.parse(fs.readFileSync(tasksPath, 'utf8'));
            res.write(`event: tasks\ndata: ${JSON.stringify(tasks)}\n\n`);
        } catch (e) {}
    }

    sseClients.add(res);

    // Keep-alive ping every 20s
    const ping = setInterval(() => {
        try { res.write(`: ping\n\n`); } catch (e) { clearInterval(ping); sseClients.delete(res); }
    }, 20000);

    req.on('close', () => {
        clearInterval(ping);
        sseClients.delete(res);
    });
});

// ── Health endpoint ──
app.get('/api/health', (req, res) => {
    broadcast('health', { status: 'ok', ts: new Date().toISOString() });
    res.json({ status: 'ok', ts: new Date().toISOString(), clients: sseClients.size });
});

// ── Task injection endpoint ──
app.post('/api/task', (req, res) => {
    try {
        const newTask = req.body;
        if (!newTask || !newTask.id) {
            return res.status(400).json({ ok: false, error: 'Missing task object or task.id' });
        }

        const tasksPath = path.join(ROOT, 'workspace', 'pending-tasks.json');
        let tasks = [];
        if (fs.existsSync(tasksPath)) {
            try { tasks = JSON.parse(fs.readFileSync(tasksPath, 'utf8')); }
            catch (err) { console.error('Error parsing pending-tasks.json:', err); tasks = []; }
        }
        tasks.push(newTask);
        fs.writeFileSync(tasksPath, JSON.stringify(tasks, null, 2));

        // Broadcast to all Nexus clients
        broadcast('task', { ...newTask, event: 'injected' });
        broadcast('log', { type: 'log', level: 'event', message: `task ${newTask.id} injected` });

        // Fire heartbeat
        exec('node aether_os/skills/heartbeat_check.js', { cwd: ROOT }, (error) => {
            if (error) console.error(`Background heartbeat trigger failed: ${error}`);
            else broadcast('heartbeat', { fired: true, ts: new Date().toISOString() });
        });

        res.json({ ok: true, id: newTask.id });
    } catch (err) {
        console.error('Error in /api/task:', err);
        res.status(500).json({ ok: false, error: 'Internal server error' });
    }
});

// ── Tasks list endpoint ──
app.get('/api/tasks', (req, res) => {
    const tasksPath = path.join(ROOT, 'workspace', 'pending-tasks.json');
    try {
        const tasks = fs.existsSync(tasksPath) ? JSON.parse(fs.readFileSync(tasksPath, 'utf8')) : [];
        res.json(tasks);
    } catch (e) {
        res.json([]);
    }
});

// ── Nexus dashboard ──
app.get('/nexus', (req, res) => {
    res.sendFile(path.join(ROOT, 'public', 'nexus.html'));
});

// ── Main chat UI ──
app.get('/', (req, res) => {
    res.sendFile(path.join(DIR, 'mist_chat.html'));
});

// ── Static assets ──
app.use(express.static(DIR));
app.use('/public', express.static(path.join(ROOT, 'public')));

// ── Start ──
app.listen(PORT, () => {
    console.log(`✧ MIST Nexus running at http://localhost:${PORT}`);
    console.log(`   Chat: http://localhost:${PORT}/`);
    console.log(`   Nexus: http://localhost:${PORT}/nexus`);
    console.log(`   Stream: http://localhost:${PORT}/api/stream`);
});
