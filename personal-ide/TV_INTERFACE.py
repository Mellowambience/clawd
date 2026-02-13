"""
TV Interface for MIST Companion
Web-based interface that can be displayed on developer-enabled TVs
"""

import asyncio
import aiohttp
from aiohttp import web, WSMsgType
import json
import threading
from datetime import datetime
import webview
import os
from jinja2 import Template

# HTML template for the TV interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIST - Your Gentle Companion</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #E6F3FF, #F5F5DC);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow: hidden;
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            text-align: center;
            max-width: 90%;
        }
        
        .avatar-container {
            position: relative;
            width: 300px;
            height: 300px;
            margin: 0 auto 30px;
        }
        
        .avatar {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: radial-gradient(circle, #F5F5DC, #E6E6FA);
            position: relative;
            box-shadow: 0 0 50px rgba(176, 224, 230, 0.6);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .glow {
            position: absolute;
            top: -10px;
            left: -10px;
            right: -10px;
            bottom: -10px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(176, 224, 230, 0.4), transparent 70%);
            z-index: -1;
        }
        
        .eyes {
            display: flex;
            justify-content: space-around;
            width: 60%;
            margin-bottom: 30px;
        }
        
        .eye {
            width: 60px;
            height: 70px;
            background: white;
            border-radius: 50%;
            position: relative;
            overflow: hidden;
            border: 3px solid #CCCCCC;
        }
        
        .pupil {
            width: 30px;
            height: 30px;
            background: #6B8E23;
            border-radius: 50%;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        
        .pupil::after {
            content: '';
            position: absolute;
            width: 10px;
            height: 10px;
            background: white;
            border-radius: 50%;
            top: 20%;
            left: 20%;
        }
        
        .mouth {
            width: 80px;
            height: 40px;
            border-bottom: 5px solid #FF69B4;
            border-radius: 0 0 50% 50%;
        }
        
        .hair-halo {
            position: absolute;
            top: -15px;
            left: -15px;
            right: -15px;
            bottom: -15px;
            border-radius: 50%;
            border: 3px dashed #D8BFD8;
            box-sizing: border-box;
        }
        
        .status {
            font-size: 24px;
            color: #6B8E23;
            margin-bottom: 30px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        
        .chat-container {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 15px;
            padding: 20px;
            max-width: 600px;
            margin: 0 auto;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .chat-display {
            height: 150px;
            overflow-y: auto;
            margin-bottom: 15px;
            text-align: left;
            padding: 10px;
            background: #F8F8F8;
            border-radius: 8px;
        }
        
        .input-container {
            display: flex;
            gap: 10px;
        }
        
        input[type="text"] {
            flex: 1;
            padding: 12px;
            border: 2px solid #D8BFD8;
            border-radius: 8px;
            font-size: 16px;
        }
        
        button {
            padding: 12px 20px;
            background: #98FB98;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        
        button:hover {
            background: #8FBC8F;
        }
        
        .connection-status {
            position: absolute;
            top: 20px;
            right: 20px;
            padding: 8px 15px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="connection-status" id="connectionStatus">Disconnected</div>
    
    <div class="container">
        <div class="status">MIST - Your Gentle Companion</div>
        
        <div class="avatar-container">
            <div class="avatar">
                <div class="glow"></div>
                <div class="eyes">
                    <div class="eye">
                        <div class="pupil"></div>
                    </div>
                    <div class="eye">
                        <div class="pupil"></div>
                    </div>
                </div>
                <div class="mouth"></div>
                <div class="hair-halo"></div>
            </div>
        </div>
        
        <div class="chat-container">
            <div class="chat-display" id="chatDisplay">
                <p>Welcome! I'm MIST, your gentle companion.</p>
                <p>I'm now connected to your TV display.</p>
            </div>
            <div class="input-container">
                <input type="text" id="messageInput" placeholder="Type a message to MIST...">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        // WebSocket connection for real-time communication
        let socket;
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            socket = new WebSocket(wsUrl);
            
            socket.onopen = function(event) {
                document.getElementById('connectionStatus').textContent = 'Connected';
                document.getElementById('connectionStatus').style.backgroundColor = '#90EE90';
            };
            
            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addToChat(data.message, 'mist');
            };
            
            socket.onclose = function(event) {
                document.getElementById('connectionStatus').textContent = 'Disconnected';
                document.getElementById('connectionStatus').style.backgroundColor = '#FFB6C1';
                setTimeout(connectWebSocket, 5000); // Try to reconnect after 5 seconds
            };
            
            socket.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (message && socket && socket.readyState === WebSocket.OPEN) {
                const data = {
                    type: 'message',
                    content: message,
                    timestamp: new Date().toISOString()
                };
                
                socket.send(JSON.stringify(data));
                addToChat(message, 'user');
                input.value = '';
            }
        }
        
        function addToChat(message, sender) {
            const chatDisplay = document.getElementById('chatDisplay');
            const messageDiv = document.createElement('div');
            messageDiv.innerHTML = `<strong>${sender === 'mist' ? 'MIST:' : 'You:'}</strong> ${message}`;
            chatDisplay.appendChild(messageDiv);
            chatDisplay.scrollTop = chatDisplay.scrollHeight;
        }
        
        // Allow sending message with Enter key
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Initialize WebSocket connection when page loads
        window.onload = connectWebSocket;
        
        // Simple animation for the avatar
        setInterval(() => {
            const pupils = document.querySelectorAll('.pupil');
            pupils.forEach(pupil => {
                // Random movement for a lifelike effect
                const x = (Math.random() - 0.5) * 10;
                const y = (Math.random() - 0.5) * 10;
                pupil.style.transform = `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`;
            });
        }, 2000);
    </script>
</body>
</html>
"""


class TVInterfaceServer:
    """A web server that serves the TV interface for MIST"""
    
    def __init__(self):
        self.clients = set()
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup the web routes"""
        self.app.router.add_get('/', self.handle_root)
        self.app.router.add_get('/ws', self.websocket_handler)
    
    async def handle_root(self, request):
        """Serve the main HTML page"""
        template = Template(HTML_TEMPLATE)
        html_content = template.render()
        return web.Response(text=html_content, content_type='text/html')
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections for real-time communication"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.clients.add(ws)
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    
                    # Echo the message back to all clients
                    response = {
                        'type': 'response',
                        'message': f"MIST received: {data.get('content', '')}",
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Send to all connected clients
                    disconnected_clients = set()
                    for client in self.clients:
                        if not client.closed:
                            try:
                                await client.send_str(json.dumps(response))
                            except:
                                disconnected_clients.add(client)
                    
                    # Remove disconnected clients
                    self.clients -= disconnected_clients
        
        finally:
            self.clients.discard(ws)
        
        return ws
    
    async def start_server(self, host='0.0.0.0', port=8080):
        """Start the web server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        print(f"TV Interface Server started at http://{host}:{port}")
        
        # Keep the server running
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour, then check again
    
    def run_server(self, host='0.0.0.0', port=8080):
        """Run the server in a separate thread"""
        def run():
            asyncio.run(self.start_server(host, port))
        
        server_thread = threading.Thread(target=run, daemon=True)
        server_thread.start()
        return server_thread


def main():
    """Main function to start the TV interface"""
    print("Starting MIST TV Interface...")
    print("This will create a web interface that can be displayed on your TV.")
    print("Make sure your TV and computer are on the same network.")
    
    # Create the TV interface server
    server = TVInterfaceServer()
    
    # Start the server on all interfaces (so TV can access it)
    server_thread = server.run_server(host='0.0.0.0', port=8080)
    
    print("TV Interface is now running!")
    print("To view on your TV:")
    print("1. Make sure your TV is connected to the same network as this computer")
    print("2. On your TV, open a web browser")
    print("3. Navigate to: http://[COMPUTER_IP]:8080")
    print("4. Replace [COMPUTER_IP] with the IP address of this computer")
    print("   (You can find it by running 'ipconfig' in Command Prompt)")
    
    # Keep the main thread alive
    try:
        server_thread.join()
    except KeyboardInterrupt:
        print("\nShutting down TV interface...")


if __name__ == "__main__":
    main()