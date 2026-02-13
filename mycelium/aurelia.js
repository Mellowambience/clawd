// ═══════════════════════════════════════════════════════════════
// AURELIA'S LATTICE // CORE CONTROLLER
// ═══════════════════════════════════════════════════════════════

const STATE = {
    tension: 0,
    nodes: 0,
    dominant: 'NEUTRAL',
    lastScan: '',
};

// 1. NEURAL VOID: THREE.JS ENGINE
const initScene = () => {
    const container = document.getElementById('shard-container');
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });

    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    // Crystal Shard
    const geometry = new THREE.OctahedronGeometry(2, 0);
    const material = new THREE.MeshPhongMaterial({
        color: 0x00f2ff,
        emissive: 0x00f2ff,
        emissiveIntensity: 0.5,
        transparent: true,
        opacity: 0.3,
        wireframe: true
    });
    const shard = new THREE.Mesh(geometry, material);
    scene.add(shard);

    // Dynamic Atmosphere
    const light = new THREE.PointLight(0xff00ea, 2, 50);
    light.position.set(10, 10, 10);
    scene.add(light);
    scene.add(new THREE.AmbientLight(0x404040, 2));

    camera.position.z = 8;

    const animate = () => {
        requestAnimationFrame(animate);
        shard.rotation.y += 0.005 + (STATE.tension * 0.05);
        shard.rotation.z += 0.002;
        shard.scale.setScalar(1 + Math.sin(Date.now() * 0.001) * 0.1);

        material.emissiveIntensity = 0.5 + (STATE.tension * 2);

        renderer.render(scene, camera);
    };
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });
};

// 2. NETWORKING: PULSE & GATEWAY
const socket = io(`http://${window.location.hostname}:8765`);
let gatewaySocket;

const initNetworking = () => {
    // Pulse Connection
    socket.on('connect', () => {
        const el = document.getElementById('stat-pulse');
        el.classList.add('active');
        el.querySelector('.val').textContent = 'SYNCED';
    });

    socket.on('disconnect', () => {
        const el = document.getElementById('stat-pulse');
        el.classList.remove('active');
        el.querySelector('.val').textContent = 'OFFLINE';
    });

    socket.on('lattice_update', (data) => {
        if (!data) return;
        STATE.tension = data.heart?.tension || 0;
        STATE.nodes = data.nodes?.length || 0;
        STATE.dominant = data.state?.dominant || 'NEUTRAL';

        document.getElementById('val-tension').textContent = STATE.tension.toFixed(2);
        document.getElementById('val-nodes').textContent = STATE.nodes;
        document.getElementById('val-dominant').textContent = STATE.dominant;

        if (data.last_scan && data.last_scan !== STATE.lastScan) {
            STATE.lastScan = data.last_scan;
            logTelemetry(data.last_scan);
        }
    });

    // Gateway Connection
    connectGateway();
};

const connectGateway = () => {
    gatewaySocket = new WebSocket(`ws://${window.location.hostname}:18789`);
    const el = document.getElementById('stat-gateway');

    gatewaySocket.onopen = () => {
        el.classList.add('active');
        el.querySelector('.val').textContent = 'RESONATING';
        gatewaySocket.send(JSON.stringify({
            type: "req",
            id: Date.now(),
            method: "connect",
            params: { auth: { token: "secret123" } }
        }));
    };

    gatewaySocket.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        const status = document.getElementById('chat-status');

        if (msg.type === 'event') {
            if (msg.event === 'thought') {
                status.textContent = `⟁ ${msg.payload.text}`;
            }
            if (msg.event === 'chat') {
                if (msg.payload.state === 'final' || msg.payload.state === 'tool_call') {
                    addMessage(msg.payload.state === 'final' ? 'mist' : 'system', msg.payload.message.content[0].text);
                }
                if (msg.payload.state === 'final') status.textContent = '';
            }
        }
    };

    gatewaySocket.onclose = () => {
        el.classList.remove('active');
        el.querySelector('.val').textContent = 'DISCONNECTED';
        setTimeout(connectGateway, 3000);
    };
};

const addMessage = (role, text) => {
    const scroller = document.getElementById('chat-scroller');
    const msg = document.createElement('div');
    msg.className = `msg-wrap ${role}`;
    msg.innerHTML = `
        <div class="msg-meta" style="font-size: 8px; color: var(--gray); margin-bottom: 4px;">${role.toUpperCase()} // ${new Date().toLocaleTimeString()}</div>
        <div class="msg-body" style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; border-left: 2px solid ${role === 'mist' ? 'var(--cyan)' : 'var(--magenta)'}; font-size: 11px;">
            ${text}
        </div>
    `;
    scroller.appendChild(msg);
    scroller.scrollTop = scroller.scrollHeight;
};

const logTelemetry = (text) => {
    const log = document.getElementById('telemetry-log');
    const entry = document.createElement('div');
    entry.style.marginBottom = '5px';
    entry.innerHTML = `<span style="color: var(--cyan);">[${new Date().toLocaleTimeString()}]</span> ${text}`;
    log.prepend(entry);
};

// 3. UI INTERACTIONS
document.getElementById('send-btn').onclick = () => {
    const input = document.getElementById('chat-input');
    const val = input.value.trim();
    if (val && gatewaySocket.readyState === WebSocket.OPEN) {
        addMessage('user', val);
        gatewaySocket.send(JSON.stringify({
            type: "req",
            id: Date.now(),
            method: "chat.send",
            params: { text: val, sessionId: "aurelia-main" }
        }));
        input.value = '';
    }
};

document.getElementById('chat-input').onkeypress = (e) => {
    if (e.key === 'Enter') document.getElementById('send-btn').click();
};

// INITIALIZE
window.onload = () => {
    initScene();
    initNetworking();
};
