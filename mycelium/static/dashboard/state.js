export const state = {
    pulseConnected: false,
    gatewayConnected: false,
    maintenance: false,
    systemState: 'unknown',
    manifestation: null,
    cosmic: null,
    nodes: [],
    reflexes: [],
    guardrailEvents: [],
    gatewayMessages: [],
    events: [],
    lastUpdate: 0,
    companion: {
        enabled: true,
        userName: '',
        tone: 'gentle',
        boundary: 'supportive, respectful, non-judgmental',
    },
};

const COMPANION_KEY = 'mycelium_companion_profile_v1';

function loadCompanionProfile() {
    try {
        const raw = window.localStorage.getItem(COMPANION_KEY);
        if (!raw) return;
        const parsed = JSON.parse(raw);
        if (!parsed || typeof parsed !== 'object') return;

        state.companion = {
            enabled: Boolean(parsed.enabled),
            userName: typeof parsed.userName === 'string' ? parsed.userName : '',
            tone: typeof parsed.tone === 'string' ? parsed.tone : 'gentle',
            boundary: typeof parsed.boundary === 'string'
                ? parsed.boundary
                : 'supportive, respectful, non-judgmental',
        };
    } catch (_err) {
        // Ignore malformed local preferences and continue with defaults.
    }
}

function persistCompanionProfile() {
    try {
        window.localStorage.setItem(COMPANION_KEY, JSON.stringify(state.companion));
    } catch (_err) {
        // Local storage may be unavailable in private mode. Ignore safely.
    }
}

loadCompanionProfile();

export function applyPayload(payload) {
    const next = payload || {};
    state.manifestation = next.manifestation || null;
    state.cosmic = next.cosmic || null;
    state.nodes = Array.isArray(next.nodes) ? next.nodes : [];
    state.reflexes = Array.isArray(next.reflexes) ? next.reflexes : [];
    state.maintenance = Boolean(next.maintenance);
    state.systemState = next.state?.dominant || state.systemState || 'unknown';
    state.lastUpdate = Date.now();
}

export function addEvent(level, message) {
    state.events.unshift({
        at: new Date().toLocaleTimeString([], { hour12: false }),
        level,
        message,
    });
    state.events = state.events.slice(0, 120);
}

export function addGatewayMessage(role, text, meta = {}) {
    state.gatewayMessages.unshift({
        at: new Date().toLocaleTimeString([], { hour12: false }),
        role,
        text,
        verifiedLocal: Boolean(meta.verifiedLocal),
        receiptId: meta.receipt?.id || null,
        kind: meta.kind || null,
    });
    state.gatewayMessages = state.gatewayMessages.slice(0, 120);
}

export function setCompanionProfile(partial) {
    state.companion = {
        ...state.companion,
        ...partial,
    };
    persistCompanionProfile();
}

export function toggleCompanionMode() {
    state.companion.enabled = !state.companion.enabled;
    persistCompanionProfile();
    return state.companion.enabled;
}
