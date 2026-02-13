function wsBaseUrl(port) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.hostname}:${port}`;
}

export function connectPulse(onPayload, onConnectionChange) {
    if (typeof io === 'undefined') {
        onConnectionChange(false, 'socket.io missing');
        return null;
    }

    const socket = io(window.location.origin, {
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionDelay: 3000,
    });

    socket.on('connect', () => onConnectionChange(true));
    socket.on('disconnect', () => onConnectionChange(false, 'socket disconnected'));
    socket.on('connect_error', (err) => onConnectionChange(false, err?.message || 'connect error'));

    const acceptPayload = (payload) => {
        if (payload && typeof payload === 'object') {
            onPayload(payload);
        }
    };

    socket.on('lattice_update', acceptPayload);
    socket.on('pulse', acceptPayload);

    return socket;
}

export async function fetchManifest() {
    const response = await fetch('/manifest', { cache: 'no-store' });
    if (!response.ok) {
        throw new Error(`manifest status ${response.status}`);
    }
    return response.json();
}

export async function fetchGuardrailEvents(limit = 40) {
    const response = await fetch(`/companion/guardrail-events?limit=${encodeURIComponent(limit)}`, { cache: 'no-store' });
    if (!response.ok) {
        throw new Error(`guardrail-events status ${response.status}`);
    }
    return response.json();
}

export async function postLocalCompanionAction(message) {
    const response = await fetch('/companion/local-action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
    });
    if (!response.ok) {
        throw new Error(`local-action status ${response.status}`);
    }
    return response.json();
}

export async function postCompanionResponseValidation(userMessage, assistantMessage) {
    const response = await fetch('/companion/validate-response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_message: userMessage,
            assistant_message: assistantMessage,
        }),
    });
    if (!response.ok) {
        throw new Error(`validate-response status ${response.status}`);
    }
    return response.json();
}

export function connectGateway(onStatus, onMessage, onThought, onError) {
    const gateway = new WebSocket(wsBaseUrl(18789));

    gateway.onopen = () => {
        onStatus(true);
        gateway.send(JSON.stringify({
            type: 'req',
            id: Date.now(),
            method: 'connect',
            params: { auth: { token: 'neural-console' } },
        }));
    };

    gateway.onclose = () => {
        onStatus(false);
    };

    gateway.onerror = () => {
        onStatus(false);
        onError('gateway socket error');
    };

    gateway.onmessage = (event) => {
        try {
            const parsed = JSON.parse(event.data);
            if (parsed?.type !== 'event') {
                return;
            }
            if (parsed.event === 'chat') {
                const text = parsed.payload?.message?.content?.[0]?.text;
                if (typeof text === 'string' && text.trim()) {
                    onMessage(text);
                }
                return;
            }
            if (parsed.event === 'thought') {
                const thought = parsed.payload?.text;
                if (typeof thought === 'string' && thought.trim()) {
                    onThought(thought);
                }
            }
        } catch (err) {
            onError(`gateway parse error: ${err}`);
        }
    };

    return {
        socket: gateway,
        send(text) {
            if (gateway.readyState !== WebSocket.OPEN) {
                return false;
            }
            gateway.send(JSON.stringify({
                type: 'req',
                id: Date.now(),
                method: 'chat.send',
                params: { message: text },
            }));
            return true;
        },
    };
}
