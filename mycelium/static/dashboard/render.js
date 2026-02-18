/* --- MIST CONSOLE RENDERER (V2) --- */

export function renderState(state) {
    const nodes = {
        pulseStatus: document.getElementById('pulseStatus'),
        avatarFrame: document.getElementById('avatarFrame'),
        systemState: document.getElementById('systemState'),
        currentThought: document.getElementById('currentThought'),
        gatewayMessages: document.getElementById('gatewayMessages'),

        // Mini Stats
        tensionValue: document.getElementById('tensionValue'),
        cpuValue: document.getElementById('cpuValue'),
        ramValue: document.getElementById('ramValue'),
    };

    // 1. Status Dot
    if (nodes.pulseStatus) {
        if (state.pulseConnected) nodes.pulseStatus.className = 'status-dot online';
        else nodes.pulseStatus.className = 'status-dot offline';
    }

    // 2. Avatar Mood & State
    if (nodes.systemState && nodes.avatarFrame) {
        const tension = state.heart?.tension || 0;
        let mood = 'calm';
        let statusText = 'Pulse steady';

        if (tension > 5) { mood = 'alert'; statusText = 'Awareness heightened'; }
        if (tension > 10) { mood = 'nervous'; statusText = 'Tension rising'; }
        if (state.maintenance) { mood = 'repair'; statusText = 'Self-healing...'; }

        // Custom override for disconnected logic
        if (!state.pulseConnected) statusText = 'Presence faint';

        nodes.avatarFrame.dataset.mood = mood;
        nodes.systemState.textContent = statusText;

        if (nodes.tensionValue) nodes.tensionValue.textContent = tension.toFixed(1);
    }

    // 3. Thoughts (Internal Monologue)
    if (nodes.currentThought && state.events && state.events.length > 0) {
        const latestInfo = state.events.slice().reverse().find(e => e.type === 'thought' || e.type === 'info');
        if (latestInfo && nodes.currentThought.textContent !== latestInfo.message) {
            // Simple update, CSS handles animation if desired
            nodes.currentThought.textContent = latestInfo.message.toLowerCase();
        }
    }

    // 4. Telemetry (Values)
    if (state.manifestation) {
        const cpu = state.manifestation.C || 0;
        const mem = state.manifestation.O || 0;

        if (nodes.cpuValue) nodes.cpuValue.textContent = `${(cpu * 100).toFixed(0)}%`;
        if (nodes.ramValue) nodes.ramValue.textContent = `${(mem * 100).toFixed(0)}%`;
    }

    // 5. Chat History
    if (nodes.gatewayMessages) {
        renderMessages(nodes.gatewayMessages, state.gatewayMessages || []);
        nodes.gatewayMessages.scrollTop = nodes.gatewayMessages.scrollHeight;
    }
}

function renderMessages(container, messages) {
    // Basic diff to avoid redraw
    if (container.childElementCount === messages.length) return;

    container.innerHTML = '';
    messages.forEach(msg => {
        const div = document.createElement('div');
        div.className = `msg ${msg.role === 'user' ? 'user-msg' : 'mist-msg'}`;

        // Simple Bold support: replace **text** with <b>text</b>
        const rawText = msg.text || msg.content || '';
        const formattedText = rawText.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');

        div.innerHTML = formattedText;
        container.appendChild(div);
    });
}

// Bind Controls Hook (unchanged logic, just re-exporting)
export function bindControls(onSend) {
    const input = document.getElementById('gatewayInput');
    const sendBtn = document.getElementById('sendGatewayBtn');

    const handleSend = () => {
        const text = input.value.trim();
        if (text) {
            onSend(text);
            input.value = '';
        }
    };

    if (sendBtn) sendBtn.onclick = handleSend;
    if (input) input.onkeydown = (e) => {
        if (e.key === 'Enter') handleSend();
    };
}
export function bindCompanionControls() { } // No-op
