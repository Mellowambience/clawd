const nodes = {
    pulseStatus: document.getElementById('pulseStatus'),
    gatewayStatus: document.getElementById('gatewayStatus'),
    lastUpdate: document.getElementById('lastUpdate'),
    quickStatusSummary: document.getElementById('quickStatusSummary'),
    companionGreeting: document.getElementById('companionGreeting'),
    systemState: document.getElementById('systemState'),
    maintenanceState: document.getElementById('maintenanceState'),
    cpuValue: document.getElementById('cpuValue'),
    ramValue: document.getElementById('ramValue'),
    coherenceValue: document.getElementById('coherenceValue'),
    cpuBar: document.getElementById('cpuBar'),
    ramBar: document.getElementById('ramBar'),
    coherenceBar: document.getElementById('coherenceBar'),
    cosmicStatus: document.getElementById('cosmicStatus'),
    cosmicAspects: document.getElementById('cosmicAspects'),
    cosmicError: document.getElementById('cosmicError'),
    cosmicAspectList: document.getElementById('cosmicAspectList'),
    nodesList: document.getElementById('nodesList'),
    reflexList: document.getElementById('reflexList'),
    guardrailCount: document.getElementById('guardrailCount'),
    guardrailEvents: document.getElementById('guardrailEvents'),
    eventLog: document.getElementById('eventLog'),
    gatewayMessages: document.getElementById('gatewayMessages'),
    gatewayInput: document.getElementById('gatewayInput'),
    sendGatewayBtn: document.getElementById('sendGatewayBtn'),
    pollManifestBtn: document.getElementById('pollManifestBtn'),
    reconnectGatewayBtn: document.getElementById('reconnectGatewayBtn'),
    gatewayHelp: document.getElementById('gatewayHelp'),
    companionStatus: document.getElementById('companionStatus'),
    companionName: document.getElementById('companionName'),
    companionTone: document.getElementById('companionTone'),
    companionBoundary: document.getElementById('companionBoundary'),
    saveCompanionBtn: document.getElementById('saveCompanionBtn'),
    toggleCompanionBtn: document.getElementById('toggleCompanionBtn'),
    avatarFrame: document.getElementById('avatarFrame'),
    avatarMood: document.getElementById('avatarMood'),
    avatarCompanionTag: document.getElementById('avatarCompanionTag'),
    avatarPulseTag: document.getElementById('avatarPulseTag'),
    avatarGatewayTag: document.getElementById('avatarGatewayTag'),
};

function setPill(element, online, onlineText, offlineText) {
    if (!element) return;
    element.classList.remove('online', 'offline', 'warning');
    element.classList.add(online ? 'online' : 'offline');
    element.textContent = online ? onlineText : offlineText;
}

function asPercent(value) {
    const normalized = Math.max(0, Math.min(1, Number(value) || 0));
    return Math.round(normalized * 100);
}

function setMeter(valueNode, barNode, rawValue) {
    const value = asPercent(rawValue);
    if (valueNode) valueNode.textContent = `${value}%`;
    if (barNode) barNode.style.width = `${value}%`;
}

function renderList(ul, items, emptyMessage, formatter) {
    if (!ul) return;
    ul.replaceChildren();

    if (!items || items.length === 0) {
        const empty = document.createElement('li');
        empty.className = 'empty';
        empty.textContent = emptyMessage;
        ul.appendChild(empty);
        return;
    }

    items.forEach((item) => {
        const row = document.createElement('li');
        row.textContent = formatter(item);
        ul.appendChild(row);
    });
}

export function bindControls(onSendGateway, onPollManifest, onReconnectGateway) {
    if (nodes.sendGatewayBtn) {
        nodes.sendGatewayBtn.addEventListener('click', () => {
            const message = nodes.gatewayInput?.value.trim() || '';
            if (!message) return;
            onSendGateway(message);
            nodes.gatewayInput.value = '';
            nodes.gatewayInput.focus();
        });
    }

    if (nodes.gatewayInput) {
        nodes.gatewayInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                nodes.sendGatewayBtn?.click();
            }
        });
    }

    if (nodes.pollManifestBtn) {
        nodes.pollManifestBtn.addEventListener('click', onPollManifest);
    }

    if (nodes.reconnectGatewayBtn) {
        nodes.reconnectGatewayBtn.addEventListener('click', () => {
            onReconnectGateway?.();
        });
    }

    document.querySelectorAll('.prompt-chip[data-prompt]').forEach((button) => {
        button.addEventListener('click', () => {
            const message = String(button.getAttribute('data-prompt') || '').trim();
            if (!message) return;
            onSendGateway(message);
            if (nodes.gatewayInput) {
                nodes.gatewayInput.value = '';
                nodes.gatewayInput.focus();
            }
        });
    });
}

export function bindCompanionControls(onSaveCompanion, onToggleCompanion) {
    if (nodes.saveCompanionBtn) {
        nodes.saveCompanionBtn.addEventListener('click', () => {
            onSaveCompanion({
                userName: nodes.companionName?.value.trim() || '',
                tone: nodes.companionTone?.value || 'gentle',
                boundary: nodes.companionBoundary?.value.trim() || 'supportive, respectful, non-judgmental',
            });
        });
    }

    if (nodes.toggleCompanionBtn) {
        nodes.toggleCompanionBtn.addEventListener('click', onToggleCompanion);
    }
}

function setValueIfNotFocused(element, value) {
    if (!element) return;
    if (document.activeElement === element) return;
    element.value = value;
}

function setAvatarTag(element, text, active) {
    if (!element) return;
    element.textContent = text;
    element.classList.remove('active', 'down');
    element.classList.add(active ? 'active' : 'down');
}

function deriveAvatarMood(state) {
    if (!state.pulseConnected) return 'offline';
    if (!state.gatewayConnected) return 'alert';

    const tone = String(state.companion?.tone || 'gentle').toLowerCase();
    if (state.companion?.enabled && tone === 'protective') return 'protective';

    const dominant = String(state.systemState || '').toLowerCase();
    if (['calm', 'warm', 'surrender'].includes(dominant)) return 'calm';
    if (['repair', 'violet'].includes(dominant)) return 'attentive';
    return 'steady';
}

function formatGuardrailTime(value) {
    if (!value) return '--:--:--';
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return '--:--:--';
    return d.toLocaleTimeString([], { hour12: false });
}

export function renderState(state) {
    setPill(nodes.pulseStatus, state.pulseConnected, 'Pulse Online', 'Pulse Offline');
    setPill(nodes.gatewayStatus, state.gatewayConnected, 'Gateway Online', 'Gateway Offline');

    if (nodes.lastUpdate) {
        const stamp = state.lastUpdate
            ? new Date(state.lastUpdate).toLocaleTimeString([], { hour12: false })
            : 'never';
        nodes.lastUpdate.textContent = `Updated: ${stamp}`;
    }

    if (nodes.systemState) {
        nodes.systemState.textContent = String(state.systemState || 'unknown');
    }

    if (nodes.quickStatusSummary) {
        if (state.pulseConnected && state.gatewayConnected) {
            nodes.quickStatusSummary.textContent = 'Both bridges are open. Speak naturally, or issue explicit local commands when you want direct execution.';
        } else if (state.pulseConnected && !state.gatewayConnected) {
            nodes.quickStatusSummary.textContent = 'Conversation bridge is reconnecting, but local actions are still available on this machine.';
        } else {
            nodes.quickStatusSummary.textContent = 'Services are warming up. You can start with simple local commands while links settle.';
        }
    }

    if (nodes.gatewayHelp) {
        nodes.gatewayHelp.classList.remove('online', 'offline');
        if (state.gatewayConnected) {
            nodes.gatewayHelp.classList.add('online');
            nodes.gatewayHelp.textContent = 'Gateway is online. Full conversation mode is available.';
        } else {
            nodes.gatewayHelp.classList.add('offline');
            nodes.gatewayHelp.textContent = 'Gateway is offline. Use local commands now, or tap Reconnect.';
        }
    }

    if (nodes.maintenanceState) {
        nodes.maintenanceState.textContent = state.maintenance ? 'on' : 'off';
    }

    const companion = state.companion || {};
    if (nodes.companionStatus) {
        nodes.companionStatus.textContent = companion.enabled ? 'enabled' : 'disabled';
    }

    if (nodes.companionGreeting) {
        const name = companion.userName?.trim() || 'friend';
        if (!companion.enabled) {
            nodes.companionGreeting.textContent = `${name}, companion mode is paused right now.`;
        } else if (state.gatewayConnected) {
            nodes.companionGreeting.textContent = `${name}, MIST is here with you and ready.`;
        } else {
            nodes.companionGreeting.textContent = `${name}, MIST is still with you while the gateway reconnects.`;
        }
    }

    setValueIfNotFocused(nodes.companionName, companion.userName || '');
    setValueIfNotFocused(nodes.companionTone, companion.tone || 'gentle');
    setValueIfNotFocused(nodes.companionBoundary, companion.boundary || 'supportive, respectful, non-judgmental');

    if (nodes.toggleCompanionBtn) {
        nodes.toggleCompanionBtn.textContent = companion.enabled ? 'Disable Companion' : 'Enable Companion';
    }

    const avatarMood = deriveAvatarMood(state);
    if (nodes.avatarFrame) {
        nodes.avatarFrame.dataset.mood = avatarMood;
    }
    if (nodes.avatarMood) {
        nodes.avatarMood.textContent = avatarMood;
    }

    setAvatarTag(
        nodes.avatarCompanionTag,
        companion.enabled ? `bond active (${companion.tone || 'gentle'})` : 'bond paused',
        Boolean(companion.enabled),
    );
    setAvatarTag(nodes.avatarPulseTag, state.pulseConnected ? 'pulse linked' : 'pulse offline', state.pulseConnected);
    setAvatarTag(
        nodes.avatarGatewayTag,
        state.gatewayConnected ? 'gateway linked' : 'gateway offline',
        state.gatewayConnected,
    );

    const m = state.manifestation || {};
    setMeter(nodes.cpuValue, nodes.cpuBar, m.F);
    setMeter(nodes.ramValue, nodes.ramBar, m.P);
    setMeter(nodes.coherenceValue, nodes.coherenceBar, m.C);

    const cosmic = state.cosmic || {};
    const cosmicOk = Boolean(cosmic.ok);
    if (nodes.cosmicStatus) {
        nodes.cosmicStatus.textContent = cosmicOk ? 'online' : 'offline';
    }
    if (nodes.cosmicAspects) {
        const count = Array.isArray(cosmic.aspects) ? cosmic.aspects.length : 0;
        nodes.cosmicAspects.textContent = String(count);
    }
    if (nodes.cosmicError) {
        nodes.cosmicError.textContent = cosmicOk ? '' : String(cosmic.error || 'ephemeris unavailable');
    }

    renderList(
        nodes.cosmicAspectList,
        Array.isArray(cosmic.aspects) ? cosmic.aspects.slice(0, 10) : [],
        'No active aspects',
        (aspect) => `${aspect.a} ${aspect.aspect} ${aspect.b} (delta ${aspect.delta})`,
    );

    renderList(
        nodes.nodesList,
        state.nodes.slice(0, 20),
        'No nodes in current payload',
        (node) => {
            const pulse = node?.pulse ?? 'n/a';
            const role = node?.role ? ` / ${node.role}` : '';
            return `${node?.id || 'node'}${role} / pulse ${pulse}`;
        },
    );

    renderList(
        nodes.reflexList,
        state.reflexes.slice(0, 20),
        'No reflex events',
        (reflex) => reflex?.msg || JSON.stringify(reflex),
    );

    const guardrailEvents = Array.isArray(state.guardrailEvents) ? state.guardrailEvents : [];
    if (nodes.guardrailCount) {
        nodes.guardrailCount.textContent = String(guardrailEvents.length);
    }

    renderList(
        nodes.guardrailEvents,
        guardrailEvents.slice(0, 30),
        'No blocked replies recorded',
        (event) => {
            const violations = Array.isArray(event?.violations) && event.violations.length
                ? event.violations.join(', ')
                : 'none';
            const intent = event?.likely_local_intent ? 'local' : 'general';
            const userText = String(event?.user_message || '').replace(/\s+/g, ' ').trim();
            const clipped = userText.length > 120 ? `${userText.slice(0, 117)}...` : userText;
            return `[${formatGuardrailTime(event?.at)}] blocked: ${violations} / intent ${intent}\nuser said: ${clipped || '(empty)'}`;
        },
    );

    renderList(
        nodes.gatewayMessages,
        state.gatewayMessages.slice(0, 50),
        'No gateway messages yet',
        (entry) => {
            if (entry.verifiedLocal && entry.role === 'mist') {
                const receipt = entry.receiptId ? ` / receipt ${entry.receiptId}` : '';
                return `[${entry.at}] MIST (local verified${receipt})\n${entry.text}`;
            }
            const who = entry.role === 'user' ? 'You' : 'MIST';
            return `[${entry.at}] ${who}\n${entry.text}`;
        },
    );

    renderList(
        nodes.eventLog,
        state.events.slice(0, 50),
        'No events recorded',
        (entry) => `[${entry.at}] ${entry.level.toUpperCase()}: ${entry.message}`,
    );
}
