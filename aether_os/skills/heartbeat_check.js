require('dotenv').config();
const { postToSlack } = require('./slack_relay');
const fs = require('fs');

async function heartbeatCheck() {
    const tasks = JSON.parse(fs.readFileSync('workspace/pending-tasks.json', 'utf8'));
    let result;
    if (tasks.length === 0) {
        result = await postToSlack('#deploy-logs', '[MIST] ✧ Heartbeat: no pending tasks.');
    } else {
        for (const task of tasks) {
            result = await postToSlack('#deploy-logs', `[MIST] ✧ Task received: ${task.title}`);
        }
    }
    console.log('Slack Response:', JSON.stringify(result, null, 2));
}

heartbeatCheck();
