import { connectPulse, fetchManifest, fetchGuardrailEvents, connectGateway, postLocalCompanionAction, postCompanionResponseValidation } from './api.js';
import { state, applyPayload, addEvent, addGatewayMessage, setCompanionProfile, toggleCompanionMode } from './state.js';
import { bindControls, bindCompanionControls, renderState } from './render.js';
import { resolveGatewayReply } from './guardrail.mjs';

const MANIFEST_POLL_MS = 5000;
const GUARDRAIL_POLL_MS = 5000;
const GATEWAY_RETRY_MS = 4000;
let pollHandle = null;
let guardrailPollHandle = null;
let gatewayReconnectHandle = null;
let gatewayReconnectAnnounced = false;
let gatewayClient = null;
let lastUserMessage = '';
let guardrailPollWarned = false;

function render() {
    renderState(state);
}

function startPolling() {
    if (pollHandle) return;

    const runPoll = async () => {
        try {
            const manifest = await fetchManifest();
            applyPayload(manifest);
            addEvent('info', 'manifest poll applied');
            render();
        } catch (error) {
            addEvent('warn', `manifest poll failed: ${error.message || error}`);
            render();
        }
    };

    runPoll();
    pollHandle = setInterval(runPoll, MANIFEST_POLL_MS);
}

function stopPolling() {
    if (!pollHandle) return;
    clearInterval(pollHandle);
    pollHandle = null;
}

async function refreshGuardrailEvents() {
    try {
        const payload = await fetchGuardrailEvents(40);
        state.guardrailEvents = Array.isArray(payload?.events) ? payload.events : [];
        guardrailPollWarned = false;
        render();
    } catch (error) {
        if (!guardrailPollWarned) {
            addEvent('warn', `guardrail feed unavailable: ${error.message || error}`);
            guardrailPollWarned = true;
            render();
        }
    }
}

function startGuardrailPolling() {
    if (guardrailPollHandle) return;
    refreshGuardrailEvents();
    guardrailPollHandle = setInterval(refreshGuardrailEvents, GUARDRAIL_POLL_MS);
}

function clearGatewayReconnect() {
    if (!gatewayReconnectHandle) return;
    clearInterval(gatewayReconnectHandle);
    gatewayReconnectHandle = null;
    gatewayReconnectAnnounced = false;
}

function scheduleGatewayReconnect(reason = '') {
    if (gatewayReconnectHandle) return;
    if (reason && !gatewayReconnectAnnounced) {
        addEvent('warn', `gateway offline: ${reason}. retrying every ${GATEWAY_RETRY_MS / 1000}s`);
        gatewayReconnectAnnounced = true;
    }

    gatewayReconnectHandle = setInterval(() => {
        if (state.gatewayConnected) {
            clearGatewayReconnect();
            return;
        }
        const readyState = gatewayClient?.socket?.readyState;
        if (readyState === WebSocket.OPEN || readyState === WebSocket.CONNECTING) {
            return;
        }
        initializeGateway();
    }, GATEWAY_RETRY_MS);
}

function reconnectGatewayNow() {
    clearGatewayReconnect();
    try {
        gatewayClient?.socket?.close();
    } catch (_err) {
        // noop
    }
    gatewayClient = null;
    initializeGateway();
    scheduleGatewayReconnect('manual reconnect');
    addEvent('info', 'manual gateway reconnect requested');
    render();
}

function onPulsePayload(payload) {
    applyPayload(payload);
    render();
}

function onPulseConnection(connected, detail = '') {
    state.pulseConnected = connected;
    if (connected) {
        stopPolling();
        addEvent('info', 'pulse socket connected');
    } else {
        startPolling();
        addEvent('warn', detail || 'pulse socket disconnected');
    }
    render();
}

function initializeGateway() {
    const readyState = gatewayClient?.socket?.readyState;
    if (readyState === WebSocket.OPEN || readyState === WebSocket.CONNECTING) {
        return;
    }
    try {
        gatewayClient = connectGateway(
            (connected) => {
                state.gatewayConnected = connected;
                if (connected) {
                    clearGatewayReconnect();
                    addEvent('info', 'gateway connected');
                } else {
                    scheduleGatewayReconnect('disconnected');
                    addEvent('warn', 'gateway disconnected');
                }
                render();
            },
            async (message) => {
                const resolved = await resolveGatewayReply({
                    userMessage: lastUserMessage,
                    assistantMessage: message,
                    validateFn: postCompanionResponseValidation,
                });
                if (resolved.source === 'client_fallback') {
                    addEvent('warn', 'response validator unavailable: using client fallback guardrail');
                }

                if (resolved.rewritten) {
                    addEvent('warn', `gateway response blocked: ${resolved.violations.join(', ') || 'guardrail'}`);
                }
                addGatewayMessage('mist', resolved.text);
                render();
            },
            (thought) => {
                addEvent('thought', thought);
                render();
            },
            (error) => {
                addEvent('warn', error);
                scheduleGatewayReconnect(error);
                render();
            },
        );
    } catch (error) {
        addEvent('warn', `gateway init failed: ${error.message || error}`);
        scheduleGatewayReconnect('init failed');
        render();
    }
}

async function sendGateway(message) {
    lastUserMessage = message;
    addGatewayMessage('user', message);

    try {
        const localResult = await postLocalCompanionAction(message);
        if (localResult?.handled) {
            if (localResult.response) {
                addGatewayMessage('mist', localResult.response, {
                    verifiedLocal: true,
                    receipt: localResult.receipt,
                    kind: localResult.kind,
                });
            }
            if (localResult.ok) {
                addEvent('info', `local action handled: ${localResult.kind || 'action'}`);
            } else {
                addEvent('warn', `local action failed: ${localResult.kind || 'error'}`);
            }
            if (localResult.receipt?.id) {
                addEvent('info', `local receipt: ${localResult.receipt.id}`);
            }
            render();
            return;
        }
    } catch (error) {
        addEvent('warn', `local action path unavailable: ${error.message || error}`);
    }

    const outbound = buildCompanionMessage(message);
    if (!gatewayClient?.send(outbound)) {
        addEvent('warn', 'gateway send failed (not connected)');
    }
    render();
}

function buildCompanionMessage(message) {
    const companion = state.companion || {};
    if (!companion.enabled) {
        return buildRealityAnchoredMessage(message, companion);
    }

    const name = companion.userName?.trim() || 'friend';
    const tone = companion.tone || 'gentle';
    const boundary = companion.boundary || 'supportive, respectful, non-judgmental';

    return buildRealityAnchoredMessage(
        [
            'COMPANION_MODE: ON',
            `COMPANION_NAME: ${name}`,
            `COMPANION_TONE: ${tone}`,
            `COMPANION_BOUNDARY: ${boundary}`,
            'Respond as MIST companion: warm, practical, emotionally safe, concise.',
            '',
            `USER_MESSAGE: ${message}`,
        ].join('\\n'),
        companion,
    );
}

function buildRealityAnchoredMessage(content, companion) {
    const name = companion?.userName?.trim() || 'friend';

    return [
        'REALITY_ANCHOR:',
        '- Runtime: OpenClawd local operator session.',
        '- Workspace root: C:\\\\Users\\\\nator\\\\clawd',
        '- You have local capabilities: read/write files, run shell commands, inspect project code.',
        '- If user requests local changes (create/edit/delete files, run commands), perform them directly and report concrete results.',
        '- Do NOT claim cloud-only limits or lack of local file access unless a real tool/permission error occurs.',
        '- If an operation fails, report exact failure briefly and propose the next concrete step.',
        '- Do not invent prior conversations; only reference verifiable session context.',
        `- You are MIST companion for ${name}.`,
        '',
        content,
    ].join('\\n');
}

function bootstrap() {
    bindControls(
        (message) => sendGateway(message),
        async () => {
            try {
                const manifest = await fetchManifest();
                applyPayload(manifest);
                addEvent('info', 'manual manifest poll complete');
                await refreshGuardrailEvents();
            } catch (error) {
                addEvent('warn', `manual poll failed: ${error.message || error}`);
            }
            render();
        },
        () => reconnectGatewayNow(),
    );

    bindCompanionControls(
        (profile) => {
            setCompanionProfile(profile);
            addEvent('info', 'companion profile saved');
            render();
        },
        () => {
            const enabled = toggleCompanionMode();
            addEvent('info', enabled ? 'companion mode enabled' : 'companion mode disabled');
            render();
        },
    );

    connectPulse(onPulsePayload, onPulseConnection);
    initializeGateway();
    scheduleGatewayReconnect('initial connect');
    startPolling();
    startGuardrailPolling();
    addEvent('info', 'dashboard initialized');
    render();
}

bootstrap();
