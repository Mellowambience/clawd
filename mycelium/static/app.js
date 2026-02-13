                // ═══════════════════════════════════════════════════════════════
                // CONFIGURATION (Loaded from global window.CONFIG)
                // ═══════════════════════════════════════════════════════════════
                const CONFIG = window.CONFIG;

                // ═══════════════════════════════════════════════════════════════
                // STATE MANAGEMENT
                // ═══════════════════════════════════════════════════════════════
                const state = {
                    pulseConnected: false,
                    mistConnected: false,
                    lastPayload: null,
                    commandHistory: [],
                    historyIndex: -1
                };

                // ═══════════════════════════════════════════════════════════════
                // UTILITY FUNCTIONS
                // ═══════════════════════════════════════════════════════════════
                function showWhisper(message, type = 'success') {
                    const whisper = document.getElementById('whisper');
                    whisper.textContent = message;
                    whisper.className = `whisper show ${type}`;
                    setTimeout(() => whisper.classList.remove('show'), 3000);
                }

                function addTerminalLine(text, type = 'output') {
                    const output = document.getElementById('terminalOutput');
                    const line = document.createElement('div');
                    line.className = `terminal-line ${type}`;
                    line.textContent = text;
                    output.appendChild(line);
                    output.scrollTop = output.scrollHeight;
                }

                function deriveLatticeMetrics(data) {
                    if (!data) return { bpm: 0, cpu: 0, ram: 0, intensity: 0, empathy: 0.5, logic: 0.5 };
                    const nodes = Array.isArray(data.nodes) ? data.nodes : [];
                    const mistNode = nodes.find(n => (n.id || '').toLowerCase() === 'mist');
                    const bpm = mistNode?.pulse || 0;
                    const cpu = (data.manifestation?.F || 0) * 100;
                    const ram = (data.manifestation?.P || 0) * 100;
                    const intensity = (data.manifestation?.I || 0) * 100;
                    const persona = data.state?.persona || {};
                    const empathy = (persona.empathy ?? 0.5) * 100;
                    const logic = (persona.logic ?? 0.5) * 100;
                    return { bpm, cpu, ram, intensity, empathy, logic };
                }

                function updateTelemetryUI(metrics) {
                    const bpmEl = document.getElementById('bpm');
                    const cpuEl = document.getElementById('cpu');
                    const ramEl = document.getElementById('ram');
                    const intensityEl = document.getElementById('intensity');
                    const empathyEl = document.getElementById('empathy');
                    const logicEl = document.getElementById('logic');

                    if (bpmEl) bpmEl.textContent = Math.round(metrics.bpm);
                    if (cpuEl) cpuEl.textContent = `${metrics.cpu.toFixed(1)}%`;
                    if (ramEl) ramEl.textContent = `${metrics.ram.toFixed(1)}%`;
                    if (intensityEl) intensityEl.textContent = `${metrics.intensity.toFixed(0)}%`;
                    if (empathyEl) empathyEl.textContent = `${metrics.empathy.toFixed(0)}%`;
                    if (logicEl) logicEl.textContent = `${metrics.logic.toFixed(0)}%`;
                }

                // ═══════════════════════════════════════════════════════════════
                // MODULE 1: LUNAR KITSUNE PROJECTION (2D Canvas - Audio Reactive)
                // ═══════════════════════════════════════════════════════════════
                const projectionCanvas = document.getElementById('projection');
                let audioContext = null;
                let analyser = null;
                let dataArray = null;
                let audioInitialized = false;

                // Audio reactive state
                const audioState = {
                    bass: 0,
                    mid: 0,
                    high: 0,
                    volume: 0,
                    beat: false
                };

                async function initAudio() {
                    if (audioInitialized) return;

                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({
                            audio: {
                                echoCancellation: false,
                                noiseSuppression: false,
                                autoGainControl: false
                            }
                        });

                        audioContext = new (window.AudioContext || window.webkitAudioContext)();
                        analyser = audioContext.createAnalyser();
                        analyser.fftSize = 512;

                        const source = audioContext.createMediaStreamSource(stream);
                        source.connect(analyser);

                        dataArray = new Uint8Array(analyser.frequencyBinCount);
                        audioInitialized = true;

                        addTerminalLine('⟁ Audio reactive mode enabled', 'output');
                        showWhisper('Faeries now respond to your music ✦');
                    } catch (e) {
                        console.error('Audio init failed:', e);
                        addTerminalLine('Audio capture unavailable - projection in static mode', 'error');
                    }
                }

                function analyzeAudio() {
                    if (!analyser || !dataArray) return;

                    analyser.getByteFrequencyData(dataArray);

                    // Split into frequency bands
                    const bassEnd = Math.floor(dataArray.length * 0.15);
                    const midEnd = Math.floor(dataArray.length * 0.5);

                    let bassSum = 0, midSum = 0, highSum = 0, totalSum = 0;

                    for (let i = 0; i < dataArray.length; i++) {
                        const val = dataArray[i] / 255;
                        totalSum += val;

                        if (i < bassEnd) bassSum += val;
                        else if (i < midEnd) midSum += val;
                        else highSum += val;
                    }

                    audioState.bass = bassSum / bassEnd;
                    audioState.mid = midSum / (midEnd - bassEnd);
                    audioState.high = highSum / (dataArray.length - midEnd);
                    audioState.volume = totalSum / dataArray.length;

                    // Simple beat detection
                    audioState.beat = audioState.bass > 0.6;
                }

                if (projectionCanvas) {
                    const ctx = projectionCanvas.getContext('2d');
                    projectionCanvas.width = 400;
                    projectionCanvas.height = 400;

                    const centerX = 200;
                    const centerY = 200;
                    let beatPulse = 0;

                    function drawKitsune() {
                        ctx.clearRect(0, 0, 400, 400);

                        // Analyze audio if available
                        if (audioInitialized) {
                            analyzeAudio();
                        }

                        const time = Date.now() * 0.001;
                        const breathe = Math.sin(time * 1.5) * 0.1;
                        const float = Math.sin(time * 0.8) * 10;

                        // Beat pulse effect
                        if (audioState.beat) {
                            beatPulse = Math.min(beatPulse + 0.3, 1);
                        } else {
                            beatPulse *= 0.85;
                        }

                        // Outer glow rings (react to volume)
                        const glowIntensity = 0.15 + audioState.volume * 0.3;
                        for (let i = 3; i >= 0; i--) {
                            ctx.beginPath();
                            ctx.arc(centerX, centerY + float, 60 + i * 20 + beatPulse * 15, 0, Math.PI * 2);
                            ctx.strokeStyle = `rgba(87, 227, 195, ${glowIntensity - i * 0.03})`;
                            ctx.lineWidth = 2 + audioState.bass * 3;
                            ctx.stroke();
                        }

                        // Scale reacts to bass + beat
                        const scale = 1 + breathe + audioState.bass * 0.3 + beatPulse * 0.2;

                        // Tail flames (dual tails) - react to mid frequencies
                        const tailIntensity = 3 + Math.floor(audioState.mid * 4);
                        for (let tail = 0; tail < 2; tail++) {
                            const tailX = centerX + (tail === 0 ? -25 : 25);
                            const tailY = centerY + float + 40;

                            for (let i = 0; i < tailIntensity; i++) {
                                const flameY = tailY + i * 10 + Math.sin(time * 3 + i) * 5;
                                const flameSize = 8 - i * 1.5 + audioState.mid * 3;
                                ctx.beginPath();
                                ctx.arc(tailX, flameY, flameSize, 0, Math.PI * 2);

                                // Color shifts with high frequencies
                                const r = 255;
                                const g = 255 - audioState.high * 80;
                                const b = 255 - audioState.high * 100 + audioState.high * 50;
                                const a = i === 0 ? 0.9 : i === 1 ? 0.7 : 0.5;

                                ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${a})`;
                                ctx.fill();
                            }
                        }

                        // Main body (circle) - pulses with bass
                        ctx.beginPath();
                        ctx.arc(centerX, centerY + float, 50 * scale, 0, Math.PI * 2);
                        ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
                        ctx.fill();

                        // Border intensity reacts to volume
                        const borderGlow = 0.6 + audioState.volume * 0.4;
                        ctx.strokeStyle = `rgba(87, 227, 195, ${borderGlow})`;
                        ctx.lineWidth = 2 + beatPulse * 2;
                        ctx.stroke();

                        // Lunar Mark (crescent on body)
                        ctx.beginPath();
                        ctx.arc(centerX, centerY + float - 5, 15, 0.5, Math.PI * 1.5);
                        ctx.strokeStyle = `rgba(87, 227, 195, ${0.9 + audioState.high * 0.1})`;
                        ctx.lineWidth = 3;
                        ctx.stroke();

                        // Eyes - glow with high frequencies
                        const eyeY = centerY + float - 5;
                        const eyeGlow = 4 + audioState.high * 2;
                        ctx.beginPath();
                        ctx.arc(centerX - 15, eyeY, eyeGlow, 0, Math.PI * 2);
                        ctx.fillStyle = `rgba(87, 227, 195, ${0.8 + audioState.high * 0.2})`;
                        ctx.fill();
                        ctx.beginPath();
                        ctx.arc(centerX + 15, eyeY, eyeGlow, 0, Math.PI * 2);
                        ctx.fillStyle = `rgba(87, 227, 195, ${0.8 + audioState.high * 0.2})`;
                        ctx.fill();

                        // Inner glow - reacts to overall volume
                        const glow = ctx.createRadialGradient(centerX, centerY + float, 0, centerX, centerY + float, 100);
                        glow.addColorStop(0, `rgba(255, 255, 255, ${0.3 + audioState.volume * 0.4})`);
                        glow.addColorStop(0.5, `rgba(87, 227, 195, ${0.15 + audioState.volume * 0.2})`);
                        glow.addColorStop(1, 'rgba(87, 227, 195, 0)');
                        ctx.fillStyle = glow;
                        ctx.fillRect(centerX - 100, centerY + float - 100, 200, 200);

                        // Particle effects - count reacts to mid frequencies
                        const particleCount = 8 + Math.floor(audioState.mid * 8);
                        for (let i = 0; i < particleCount; i++) {
                            const angle = (time + i) * (0.5 + audioState.bass * 0.5);
                            const radius = 80 + Math.sin(time * 2 + i) * 10 + audioState.volume * 20;
                            const px = centerX + Math.cos(angle) * radius;
                            const py = centerY + float + Math.sin(angle) * radius;

                            ctx.beginPath();
                            ctx.arc(px, py, 2 + beatPulse * 2, 0, Math.PI * 2);
                            ctx.fillStyle = `rgba(87, 227, 195, ${0.4 + Math.sin(time * 3 + i) * 0.3 + audioState.volume * 0.3})`;
                            ctx.fill();
                        }

                        requestAnimationFrame(drawKitsune);
                    }

                    drawKitsune();

                    // Auto-enable audio on first user interaction
                    let audioEnabled = false;
                    const enableAudio = () => {
                        if (!audioEnabled) {
                            initAudio();
                            audioEnabled = true;
                            document.removeEventListener('click', enableAudio);
                            document.removeEventListener('keydown', enableAudio);
                        }
                    };
                    document.addEventListener('click', enableAudio);
                    document.addEventListener('keydown', enableAudio);
                }

                // ═══════════════════════════════════════════════════════════════
                // MODULE 2: TERMINAL & COMMAND SYSTEM
                // ═══════════════════════════════════════════════════════════════
                const terminalInput = document.getElementById('terminalInput');

                function executeCommand(cmd) {
                    state.commandHistory.push(cmd);
                    state.historyIndex = state.commandHistory.length;
                    addTerminalLine(`⟁ ${cmd}`, 'command');

                    // Check for MIST prefix
                    if (cmd.toLowerCase().startsWith('mist ')) {
                        const query = cmd.substring(5).trim();
                        sendToMist(query);
                        return;
                    }

                    // Basic command routing
                    const [command, ...args] = cmd.trim().split(/\s+/);

                    switch (command.toLowerCase()) {
                        case 'help':
                            addTerminalLine('Available commands:');
                            addTerminalLine('  help - Show this help');
                            addTerminalLine('  status - Show system status');
                            addTerminalLine('  clear - Clear console');
                            addTerminalLine('  echo <text> - Echo text');
                            addTerminalLine('  mist <query> - Ask MIST directly');
                            addTerminalLine('  bridge - Reconnect MIST bridge');
                            addTerminalLine('  export - Export memory');
                            break;

                        case 'status': {
                            const metrics = deriveLatticeMetrics(state.lastPayload);
                            addTerminalLine(`System: ${state.lastPayload?.state?.dominant || 'Unknown'}`);
                            addTerminalLine(`CPU: ${metrics.cpu.toFixed(1)}%`);
                            addTerminalLine(`RAM: ${metrics.ram.toFixed(1)}%`);
                            addTerminalLine(`BPM: ${Math.round(metrics.bpm)}`);
                            addTerminalLine(`MIST Bridge: ${state.mistConnected ? 'Connected' : 'Disconnected'}`);
                            break;
                        }

                        case 'clear':
                            document.getElementById('terminalOutput').innerHTML = '';
                            break;

                        case 'echo':
                            addTerminalLine(args.join(' '));
                            break;

                        case 'bridge':
                            connectMistBridge();
                            break;

                        case 'export':
                            exportMemory();
                            break;

                        default:
                            addTerminalLine(`Unknown command: ${command}`, 'error');
                            addTerminalLine('Type "help" for available commands');
                    }
                }

                // Terminal input handling
                if (terminalInput) {
                    terminalInput.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            const cmd = terminalInput.value.trim();
                            if (cmd) {
                                executeCommand(cmd);
                                terminalInput.value = '';
                            }
                        } else if (e.key === 'ArrowUp') {
                            e.preventDefault();
                            if (state.historyIndex > 0) {
                                state.historyIndex--;
                                terminalInput.value = state.commandHistory[state.historyIndex] || '';
                            }
                        } else if (e.key === 'ArrowDown') {
                            e.preventDefault();
                            if (state.historyIndex < state.commandHistory.length - 1) {
                                state.historyIndex++;
                                terminalInput.value = state.commandHistory[state.historyIndex] || '';
                            } else {
                                state.historyIndex = state.commandHistory.length;
                                terminalInput.value = '';
                            }
                        }
                    });
                }

                // ═══════════════════════════════════════════════════════════════
                // MODULE 3: MIST BRIDGE (WebSocket to Gateway)
                // ═══════════════════════════════════════════════════════════════
                let mistBridge = null;

                function connectMistBridge() {
                    if (mistBridge && mistBridge.readyState === WebSocket.OPEN) {
                        addTerminalLine('MIST Bridge already connected');
                        return;
                    }

                    try {
                        mistBridge = new WebSocket(CONFIG.MIST_GATEWAY);

                        mistBridge.onopen = () => {
                            state.mistConnected = true;
                            addTerminalLine('⟁ MIST Bridge Active', 'output');
                            document.getElementById('bridgeStatus').textContent = '• Connected';

                            // Send handshake
                            mistBridge.send(JSON.stringify({
                                type: 'req',
                                id: Date.now(),
                                method: 'connect',
                                params: { auth: { token: 'neural-console' } }
                            }));
                        };

                        mistBridge.onmessage = (event) => {
                            try {
                                const data = JSON.parse(event.data);
                                if (data.type === 'event' && data.event === 'chat') {
                                    const content = data.payload?.message?.content?.[0]?.text || '';
                                    if (content && data.payload.state === 'stream') {
                                        addTerminalLine(content, 'output');
                                    }
                                }
                            } catch (e) {
                                console.error('MIST Bridge parse error:', e);
                            }
                        };

                        mistBridge.onerror = () => {
                            state.mistConnected = false;
                            addTerminalLine('MIST Bridge error', 'error');
                            document.getElementById('bridgeStatus').textContent = '• Error';
                        };

                        mistBridge.onclose = () => {
                            state.mistConnected = false;
                            mistBridge = null;
                            addTerminalLine('MIST Bridge disconnected', 'error');
                            document.getElementById('bridgeStatus').textContent = '• Disconnected';

                            // Auto-reconnect
                            setTimeout(connectMistBridge, CONFIG.MIST_RECONNECT_DELAY);
                        };
                    } catch (e) {
                        addTerminalLine(`Failed to connect MIST Bridge: ${e.message}`, 'error');
                    }
                }

                function sendToMist(query) {
                    if (mistBridge && mistBridge.readyState === WebSocket.OPEN) {
                        mistBridge.send(JSON.stringify({
                            type: 'req',
                            id: Date.now(),
                            method: 'chat.send',
                            params: { message: query }
                        }));
                    } else {
                        addTerminalLine('MIST Bridge not connected. Type "bridge" to connect.', 'error');
                        connectMistBridge();
                    }
                }

                let manifestPollTimer = null;
                async function pollManifestOnce() {
                    try {
                        const res = await fetch(`${CONFIG.PULSE_SERVER}/manifest`);
                        const data = await res.json();
                        if (data && data.manifestation) {
                            const fallback = {
                                manifestation: data.manifestation,
                                state: { dominant: 'calm', persona: {} },
                                nodes: []
                            };
                            state.lastPayload = fallback;
                            const metrics = deriveLatticeMetrics(fallback);
                            updateTelemetryUI(metrics);
                        }
                    } catch (e) {
                        console.warn('Manifest poll failed:', e);
                    }
                }

                function startManifestFallback() {
                    if (manifestPollTimer) return;
                    pollManifestOnce();
                    manifestPollTimer = setInterval(pollManifestOnce, 5000);
                }

                // ═══════════════════════════════════════════════════════════════
                // MODULE 4: PULSE SERVER (Socket.IO for Telemetry)
                // ═══════════════════════════════════════════════════════════════
                function connectPulseServer() {
                    if (typeof io === 'undefined') {
                        console.error('Socket.IO not loaded');
                        startManifestFallback();
                        return;
                    }

                    const socket = io(CONFIG.PULSE_SERVER, {
                        reconnection: true,
                        reconnectionDelay: CONFIG.PULSE_RECONNECT_DELAY
                    });

                    socket.on('connect', () => {
                        state.pulseConnected = true;
                        console.log('Pulse server connected');
                        if (manifestPollTimer) {
                            clearInterval(manifestPollTimer);
                            manifestPollTimer = null;
                        }
                        const statusEl = document.getElementById('networkStatus');
                        if (statusEl) statusEl.textContent = 'Stable';
                        const dot = document.querySelector('.left-panel .status-dot');
                        if (dot) dot.className = 'status-dot stable';
                    });

                    socket.on('connect_error', () => {
                        startManifestFallback();
                    });

                    const applyLatticeUpdate = (data) => {
                        state.lastPayload = data;

                        const metrics = deriveLatticeMetrics(data);
                        updateTelemetryUI(metrics);

                        if (data.state) {
                            const stateEl = document.getElementById('systemState');
                            if (stateEl) stateEl.textContent = data.state.dominant || 'Unknown';
                        }

                        const memoryEl = document.getElementById('memoryDepth');
                        if (memoryEl) {
                            const count = Array.isArray(data.petals) ? data.petals.length : 0;
                            memoryEl.textContent = String(count);
                        }

                        const statusEl = document.getElementById('networkStatus');
                        if (statusEl) statusEl.textContent = 'Stable';
                        const dot = document.querySelector('.left-panel .status-dot');
                        if (dot) dot.className = 'status-dot stable';
                    };

                    // Primary event from current Pulse server
                    socket.on('lattice_update', applyLatticeUpdate);
                    // Back-compat if older emitter is used
                    socket.on('pulse', applyLatticeUpdate);

                    socket.on('disconnect', () => {
                        state.pulseConnected = false;
                        console.log('Pulse server disconnected');
                        const statusEl = document.getElementById('networkStatus');
                        if (statusEl) statusEl.textContent = 'Unstable';
                        const dot = document.querySelector('.left-panel .status-dot');
                        if (dot) dot.className = 'status-dot unstable';
                    });
                }

                // ═══════════════════════════════════════════════════════════════
                // MODULE 5: INTERACTIVE CONTROLS
                // ═══════════════════════════════════════════════════════════════
                async function postToBackend(endpoint, data = {}) {
                    try {
                        const res = await fetch(`${CONFIG.PULSE_SERVER}${endpoint}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(data)
                        });
                        const result = await res.json();
                        return result;
                    } catch (e) {
                        console.error(`POST ${endpoint} failed:`, e);
                        return { ok: false, error: e.message };
                    }
                }

                // Reflex Toggle
                let reflexEnabled = localStorage.getItem('mist_reflex') !== 'false';
                const reflexBtn = document.getElementById('reflexBtn');
                if (reflexBtn) {
                    if (reflexEnabled) reflexBtn.classList.add('active');

                    reflexBtn.addEventListener('click', async () => {
                        reflexEnabled = !reflexEnabled;
                        reflexBtn.classList.toggle('active', reflexEnabled);
                        localStorage.setItem('mist_reflex', reflexEnabled);

                        const result = await postToBackend('/manifest/reflex', { enabled: reflexEnabled });
                        showWhisper(reflexEnabled ? 'Reflexes active' : 'Reflexes dampened');
                    });
                }

                // Export Memory
                const exportBtn = document.getElementById('exportBtn');
                if (exportBtn) {
                    exportBtn.addEventListener('click', () => exportMemory());
                }

                async function exportMemory() {
                    try {
                        const result = await postToBackend('/export');
                        if (result.ok) {
                            showWhisper('Memory vault updated ✦');
                            addTerminalLine('Memory exported successfully');
                        } else {
                            showWhisper('Export failed', 'error');
                            addTerminalLine('Export failed: ' + result.error, 'error');
                        }
                    } catch (e) {
                        showWhisper('Connection to vault lost', 'error');
                        addTerminalLine('Export error: ' + e.message, 'error');
                    }
                }

                // Inspector (placeholder)
                const inspectorBtn = document.getElementById('inspectorBtn');
                if (inspectorBtn) {
                    inspectorBtn.addEventListener('click', () => {
                        showWhisper('Inspector not yet implemented');
                    });
                }

                // ═══════════════════════════════════════════════════════════════
                // INITIALIZATION
                // ═══════════════════════════════════════════════════════════════
                document.addEventListener('DOMContentLoaded', () => {
                    // Welcome message
                    setTimeout(() => {
                        addTerminalLine('✧ Lunar Kitsune Neural Interface Online', 'output');
                        addTerminalLine('Type "help" for commands or "mist <query>" for AI assistance', 'output');
                        addTerminalLine('Initializing connections...');

                        // Connect to services
                        connectMistBridge();
                        connectPulseServer();
                    }, 500);
                });
            
