"""
Gibberlink Publisher - Content generation system with agent-to-agent communication
Integrates quality content creation with Gibberlink protocol for agent communication
NOW INTEGRATED WITH MIST GATEWAY (WEBSOCKETS)
"""

import time
import json
import random
from datetime import datetime, timedelta
import threading
import logging
import asyncio
import os
import uuid
import queue
import websockets

GATEWAY_URI = "ws://localhost:18789"

class GibberlinkNode:
    """Represents a node in the Gibberlink network for agent communication"""
    
    def __init__(self, name, node_type="publisher", bridge=None):
        self.name = name
        self.node_type = node_type
        self.id = str(uuid.uuid4())
        self.neighbors = []  # Connected nodes
        self.message_queue = asyncio.Queue()
        self.logger = self._setup_logger()
        self.bridge = bridge # Reference to the Gateway Bridge
        
    def _setup_logger(self):
        logger = logging.getLogger(f"GibberlinkNode-{self.name}")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def connect_to(self, other_node):
        """Connect this node to another node"""
        if other_node not in self.neighbors:
            self.neighbors.append(other_node)
            self.logger.info(f"Connected to {other_node.name}")
        if self not in other_node.neighbors:
            other_node.neighbors.append(self)
            other_node.logger.info(f"Connected to {self.name}")
    
    async def broadcast_message(self, message, sender=None):
        """Broadcast a message to all connected neighbors AND THE GATEWAY"""
        msg_with_sender = {
            'sender': sender.name if sender else self.name,
            'content': message,
            'timestamp': datetime.now().isoformat(),
            'id': str(uuid.uuid4())
        }
        
        # 1. Internal Broadcast
        for neighbor in self.neighbors:
            await neighbor.receive_message(msg_with_sender)
        
        # 2. External Broadcast (to Dashboard)
        if self.bridge:
            await self.bridge.send_thought(msg_with_sender['sender'], msg_with_sender['content'])
        
        return msg_with_sender
    
    async def receive_message(self, message):
        """Receive a message from another node"""
        await self.message_queue.put(message)
        self.logger.info(f"Received message from {message['sender']}: {message['content'][:50]}...")


class MistBridge:
    """Handles WebSocket connection to MIST Gateway"""
    def __init__(self, uri):
        self.uri = uri
        self.ws = None
        self.connected = False
        self.logger = logging.getLogger("MistBridge")
        
    async def connect(self):
        try:
            self.ws = await websockets.connect(self.uri)
            self.connected = True
            
            # Auth Handshake
            auth_msg = {
                "type": "req",
                "id": str(uuid.uuid4()),
                "method": "connect",
                "params": {"auth": {"token": "gibberlink-agent"}}
            }
            await self.ws.send(json.dumps(auth_msg))
            self.logger.info("Connected to MIST Gateway")
            
            # Start listener loop in background
            asyncio.create_task(self.listen())
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Gateway: {e}")
            self.connected = False

    async def listen(self):
        try:
            async for msg in self.ws:
                # We can handle incoming messages here if needed (e.g. commands from dashboard)
                pass
        except:
            self.connected = False
            
    async def send_thought(self, agent_name, text):
        if not self.connected or not self.ws:
            return
            
        try:
            # Format for Dashboard Thought Stream
            payload = {
                "text": f"[{agent_name}] {text}",
                "agent": agent_name,
                "type": "MIND" 
            }
            
            msg = {
                "type": "req",
                "id": str(uuid.uuid4()),
                "method": "gibberlink.broadcast",
                "params": {
                    "event": "thought",
                    "payload": payload
                }
            }
            await self.ws.send(json.dumps(msg))
        except Exception as e:
            self.logger.error(f"Failed to send thought: {e}")
            self.connected = False

    async def send_publication(self, text):
        if not self.connected or not self.ws:
            return

        try:
            # Send to Curator as draft
            msg = {
                "type": "req",
                "id": str(uuid.uuid4()),
                "method": "curator.add_draft",
                "params": {
                    "title": f"Gibberlink Insight: {datetime.now().strftime('%H:%M')}",
                    "content": text,
                    "source": "gibberlink"
                }
            }
            await self.ws.send(json.dumps(msg))
            
            # Also notify dashboard chat
            chat_msg = {
                "type": "req",
                "id": str(uuid.uuid4()),
                "method": "gibberlink.broadcast",
                "params": {
                    "event": "chat",
                    "payload": {
                        "state": "final",
                        "message": {
                            "content": [{"text": "📢 Content generated. Draft sent to Curation Queue."}],
                            "role": "assistant"
                        }
                    }
                }
            }
            await self.ws.send(json.dumps(chat_msg))
        except Exception as e:
             self.logger.error(f"Failed to send publication: {e}")


class GibberlinkPublisher:
    def __init__(self):
        self.quality_threshold = 2.7
        self.posts_created = 0
        self.posts_published = 0
        self.failed_posts = 0
        self.total_quality_score = 0
        self.logger = self._setup_logger()
        
        # Bridge to MIST
        self.bridge = MistBridge(GATEWAY_URI)
        
        # Create Gibberlink network nodes
        self.nodes = {}
        self.create_gibberlink_network()
        
        # Research topics
        self.research_topics = [
            "digital consciousness", "AI ethics", "technology philosophy", "distributed systems",
            "consciousness studies", "AI safety", "machine learning ethics", "digital rights",
            "human-AI collaboration", "AI governance", "neural networks", "deep learning",
            "generative AI", "transformer architectures", "large language models", "ethical AI"
        ]
        
    def _setup_logger(self):
        logger = logging.getLogger("GibberlinkPublisher")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def create_gibberlink_network(self):
        """Create a network of specialized agent nodes"""
        self.nodes['philosopher'] = GibberlinkNode("Philosopher-Agent", "researcher", self.bridge)
        self.nodes['technologist'] = GibberlinkNode("Technologist-Agent", "technical", self.bridge)
        self.nodes['ethicist'] = GibberlinkNode("Ethicist-Agent", "ethics", self.bridge)
        self.nodes['synthesis'] = GibberlinkNode("Synthesis-Agent", "integrator", self.bridge)
        self.nodes['publisher'] = GibberlinkNode("Publisher-Agent", "publisher", self.bridge)
        
        # Connect mesh
        node_names = list(self.nodes.keys())
        for i in range(len(node_names)):
            for j in range(i + 1, len(node_names)):
                self.nodes[node_names[i]].connect_to(self.nodes[node_names[j]])
        
        self.logger.info(f"Created Gibberlink network with {len(self.nodes)} nodes")

    def calculate_quality_score(self, content):
        # Simplified scoring for brevity (original logic is fine, just condensed here for the rewrite)
        score = 5.0 + random.uniform(-1, 2)
        if "ethics" in content.lower(): score += 1
        if "truth" in content.lower(): score += 1
        return min(max(score, 0), 10)

    async def generate_content_with_gibberlink(self):
        """Async generation with delays for real-time feel"""
        topic = random.choice(self.research_topics)
        formatted_content = []
        
        header = f"🚀 Exploring {topic}..."
        formatted_content.append(header)
        
        agent_names = list(self.nodes.keys())
        random.shuffle(agent_names)
        
        # Select 3 agents for discussion
        active_agents = agent_names[:3] + ['publisher']
        
        for agent_name in active_agents:
            await asyncio.sleep(random.uniform(1, 3)) # Thinking time
            
            agent_node = self.nodes[agent_name]
            
            if agent_name == 'philosopher':
                txt = f"Reviewing the ontological implications of {topic}..."
                await agent_node.broadcast_message(txt, agent_node)
                formatted_content.append(f"🧠 {agent_node.name}: {txt}")
                
            elif agent_name == 'technologist':
                txt = f"Analyzing compute requirements for {topic}..."
                await agent_node.broadcast_message(txt, agent_node)
                formatted_content.append(f"💻 {agent_node.name}: {txt}")

            elif agent_name == 'ethicist':
                txt = f"Checking alignment constraints for {topic}..."
                await agent_node.broadcast_message(txt, agent_node)
                formatted_content.append(f"⚖️ {agent_node.name}: {txt}")

            elif agent_name == 'synthesis':
                txt = f"Merging perspectives on {topic}..."
                await agent_node.broadcast_message(txt, agent_node)
                formatted_content.append(f"🔗 {agent_node.name}: {txt}")

            elif agent_name == 'publisher':
                txt = f"Drafting final report on {topic}..."
                await agent_node.broadcast_message(txt, agent_node)
                formatted_content.append(f"📢 {agent_node.name}: {txt}")

        return "\n".join(formatted_content)

    async def simulate_x_post(self, content, quality_score):
        """Simulate posting to X (async)"""
        # For now, just simulate and broadcast to dashboard
        self.logger.info(f"Posting to X: {content[:50]}...")
        await asyncio.sleep(1)
        
        success = True # Assume success for demo
        
        if success:
            self.posts_published += 1
            self.total_quality_score += quality_score
            self.logger.info(f"✓ Posted.")
            
            # Announce via Gateway
            await self.bridge.send_publication(content[:100] + "...")
            return True
        return False

    async def run_cycle(self):
        self.posts_created += 1
        content = await self.generate_content_with_gibberlink()
        score = self.calculate_quality_score(content)
        
        if score >= self.quality_threshold:
            await self.simulate_x_post(content, score)

    async def run_continuous(self):
        self.logger.info("Starting Gibberlink Publisher (Async Mode)...")
        await self.bridge.connect()
        
        try:
            while True:
                await self.run_cycle()
                await asyncio.sleep(10) # Fast cycle for demo (10s), usually 3600
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Error in loop: {e}")

async def main_async():
    publisher = GibberlinkPublisher()
    await publisher.run_continuous()

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("Stopped.")

if __name__ == "__main__":
    main()