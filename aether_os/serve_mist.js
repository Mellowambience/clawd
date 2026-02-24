const express = require('express');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const PORT = 3333;
const DIR = __dirname;

// Use Express's existing json middleware
app.use(express.json());

// API Task Endpoint
app.post('/api/task', (req, res) => {
    try {
        const newTask = req.body;
        if (!newTask || !newTask.id) {
            return res.status(400).json({ ok: false, error: 'Missing task object or task.id' });
        }

        const tasksPath = path.join(DIR, '..', 'workspace', 'pending-tasks.json');
        let tasks = [];

        // Read workspace/pending-tasks.json (create with [] if missing)
        if (fs.existsSync(tasksPath)) {
            try {
                tasks = JSON.parse(fs.readFileSync(tasksPath, 'utf8'));
            } catch (err) {
                console.error('Error parsing pending-tasks.json, resetting to []:', err);
                tasks = [];
            }
        }

        // Append the task object
        tasks.push(newTask);

        // Write the file back
        fs.writeFileSync(tasksPath, JSON.stringify(tasks, null, 2));

        // Immediately trigger one heartbeat_check.js run (non-blocking, fire-and-forget)
        exec('node aether_os/skills/heartbeat_check.js', { cwd: path.join(DIR, '..') }, (error) => {
            if (error) console.error(`Background heartbeat trigger failed: ${error}`);
        });

        // Returns { ok: true, id: task.id }
        res.json({ ok: true, id: newTask.id });
    } catch (err) {
        console.error('Error in /api/task:', err);
        res.status(500).json({ ok: false, error: 'Internal server error' });
    }
});

// Main route serves mist_chat.html
app.get('/', (req, res) => {
    res.sendFile(path.join(DIR, 'mist_chat.html'));
});

// Static assets from current directory
app.use(express.static(DIR));

app.listen(PORT, () => {
    console.log(`✧ MIST Chat Server running at http://localhost:${PORT}`);
    console.log('   Open this URL in your browser to connect to MIST.');
});
