// slack_relay.js — posts a message to a Slack channel via bot token

async function postToSlack(channel, text) {
    const token = process.env.SLACK_BOT_TOKEN;
    if (!token) {
        throw new Error('SLACK_BOT_TOKEN is not defined in environment variables');
    }

    const res = await fetch('https://slack.com/api/chat.postMessage', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json; charset=utf-8'
        },
        body: JSON.stringify({ channel, text })
    });
    return res.json();
}

module.exports = { postToSlack };
