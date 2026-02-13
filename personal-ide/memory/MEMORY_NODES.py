"""
Memory Web Component for MIST Companion Intelligence
Implements distributed memory system with spiderweb architecture
"""

import asyncio
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

from integration.CORE_HUB import Message, ComponentType, CoreHub
from visualization.VISUAL_COMPANION import VisualCompanion
from voice.VOICE_SYNTHESIZER import VoiceSynthesizer


class MemoryType(Enum):
    """Types of memory nodes"""
    IDENTITY = "identity"
    INTERACTION = "interaction"
    KNOWLEDGE = "knowledge"
    PROJECT = "project"
    EMOTIONAL = "emotional"
    CONTEXTUAL = "contextual"


class MemoryImportance(Enum):
    """Levels of memory importance"""
    BACKGROUND = 1  # Low importance, easily forgettable
    NORMAL = 2      # Regular memories
    IMPORTANT = 3   # Important but not critical
    CRITICAL = 4    # Critical memories that should be retained


@dataclass
class MemoryNode:
    """A single node in the memory web"""
    id: str
    content: Any
    memory_type: MemoryType
    timestamp: datetime
    importance: MemoryImportance
    tags: List[str] = field(default_factory=list)
    connections: List[str] = field(default_factory=list)  # IDs of connected nodes
    context: Dict[str, Any] = field(default_factory=dict)
    retention_score: float = 1.0  # 0.0 to 1.0, higher means more likely to be retained
    last_accessed: datetime = field(default_factory=datetime.now)


@dataclass
class MemoryQuery:
    """Structure for querying memory nodes"""
    text_query: str = ""
    memory_types: List[MemoryType] = field(default_factory=list)
    time_range: Optional[tuple] = None  # (start_time, end_time)
    tags: List[str] = field(default_factory=list)
    importance_threshold: MemoryImportance = MemoryImportance.NORMAL
    max_results: int = 10


class MemoryConsolidator:
    """Handles memory consolidation and transfer between short-term and long-term"""
    
    def __init__(self):
        self.daily_threshold = timedelta(hours=24)
        self.consolidation_interval = timedelta(minutes=30)
        self.last_consolidation = datetime.now()
    
    def should_consolidate(self) -> bool:
        """Check if it's time to consolidate memories"""
        return datetime.now() - self.last_consolidation >= self.consolidation_interval
    
    def consolidate_daily_to_wisdom(self, daily_nodes: List[MemoryNode]) -> List[MemoryNode]:
        """Consolidate daily memories into wisdom nodes"""
        consolidated = []
        
        for node in daily_nodes:
            # Only consolidate important memories
            if node.importance.value >= MemoryImportance.IMPORTANT.value:
                # Create a summary node
                summary_node = MemoryNode(
                    id=f"wisdom_{uuid.uuid4()}",
                    content=f"Summary of: {str(node.content)[:100]}...",
                    memory_type=MemoryType.KNOWLEDGE,
                    timestamp=datetime.now(),
                    importance=MemoryImportance.CRITICAL,
                    tags=["consolidated", "summary"] + node.tags,
                    context={**node.context, "original_id": node.id, "consolidation_date": datetime.now().isoformat()},
                    retention_score=min(1.0, node.retention_score + 0.3)
                )
                consolidated.append(summary_node)
        
        self.last_consolidation = datetime.now()
        return consolidated


class AssociativeLinker:
    """Creates associative links between related memory nodes"""
    
    def __init__(self):
        self.similarity_threshold = 0.7
        self.max_connections_per_node = 10
    
    def find_similar_nodes(self, target_node: MemoryNode, candidates: List[MemoryNode]) -> List[str]:
        """Find nodes similar to the target node"""
        similar_ids = []
        
        for candidate in candidates:
            if target_node.id == candidate.id:
                continue  # Don't connect to self
            
            similarity = self.calculate_similarity(target_node, candidate)
            if similarity >= self.similarity_threshold:
                similar_ids.append(candidate.id)
                
                # Limit connections per node
                if len(similar_ids) >= self.max_connections_per_node:
                    break
        
        return similar_ids
    
    def calculate_similarity(self, node1: MemoryNode, node2: MemoryNode) -> float:
        """Calculate similarity between two memory nodes"""
        score = 0.0
        
        # Tag overlap contributes to similarity
        if node1.tags and node2.tags:
            common_tags = set(node1.tags) & set(node2.tags)
            tag_overlap = len(common_tags) / max(len(node1.tags), len(node2.tags))
            score += tag_overlap * 0.4
        
        # Type matching contributes to similarity
        if node1.memory_type == node2.memory_type:
            score += 0.3
        
        # Content similarity (basic string comparison)
        content1 = str(node1.content).lower()
        content2 = str(node2.content).lower()
        
        # Simple word overlap
        words1 = set(content1.split())
        words2 = set(content2.split())
        if words1 and words2:
            word_overlap = len(words1 & words2) / max(len(words1), len(words2))
            score += word_overlap * 0.3
        
        return min(1.0, score)


class MemoryPruner:
    """Manages removal of weak or irrelevant memory connections"""
    
    def __init__(self):
        self.retention_threshold = 0.3
        self.time_decay_factor = 0.01  # Per day
        self.min_connection_strength = 0.2
    
    def evaluate_for_pruning(self, nodes: List[MemoryNode], connections: Dict[str, List[str]]) -> List[str]:
        """Evaluate nodes for potential pruning"""
        nodes_to_remove = []
        
        for node in nodes:
            # Check retention score
            if node.retention_score < self.retention_threshold:
                # Apply time decay
                days_since_creation = (datetime.now() - node.timestamp).days
                decayed_score = node.retention_score - (days_since_creation * self.time_decay_factor)
                
                if decayed_score < self.retention_threshold:
                    nodes_to_remove.append(node.id)
        
        return nodes_to_remove
    
    def prune_weak_connections(self, connections: Dict[str, List[str]], connection_strengths: Dict[str, Dict[str, float]]) -> Dict[str, List[str]]:
        """Remove weak connections between nodes"""
        pruned_connections = {}
        
        for node_id, connected_nodes in connections.items():
            strong_connections = []
            
            for connected_id in connected_nodes:
                strength = connection_strengths.get(node_id, {}).get(connected_id, 0.0)
                if strength >= self.min_connection_strength:
                    strong_connections.append(connected_id)
            
            pruned_connections[node_id] = strong_connections
        
        return pruned_connections


class MemoryWeb:
    """Main class for the distributed memory system"""
    
    def __init__(self, hub: CoreHub, visual_companion: VisualCompanion = None, voice_synthesizer: VoiceSynthesizer = None):
        self.hub = hub
        self.visual_companion = visual_companion
        self.voice_synthesizer = voice_synthesizer
        self.name = "memory_web"
        self.component_type = ComponentType.MEMORY
        self.active = True
        
        # Initialize memory components
        self.nodes: Dict[str, MemoryNode] = {}
        self.type_index: Dict[MemoryType, List[str]] = {mt: [] for mt in MemoryType}
        self.tag_index: Dict[str, List[str]] = {}
        self.connections: Dict[str, List[str]] = {}
        self.connection_strengths: Dict[str, Dict[str, float]] = {}  # {node_id: {connected_id: strength}}
        
        # Memory management components
        self.consolidator = MemoryConsolidator()
        self.associative_linker = AssociativeLinker()
        self.pruner = MemoryPruner()
        
        # State tracking
        self.stats = {
            "total_nodes": 0,
            "daily_nodes": 0,
            "wisdom_nodes": 0,
            "total_connections": 0
        }
        
        # Register with the hub
        self.hub.registry.register_component(
            self.name,
            self.handle_message,
            self.component_type
        )
        
        # Register for relevant events
        self.hub.event_coord.register_event_handler("store_memory", self.on_store_memory)
        self.hub.event_coord.register_event_handler("retrieve_memory", self.on_retrieve_memory)
        self.hub.event_coord.register_event_handler("context_update", self.on_context_update)
        self.hub.event_coord.register_event_handler("system_maintenance", self.on_maintenance)
    
    def create_memory_node(self, content: Any, memory_type: MemoryType, importance: MemoryImportance, tags: List[str] = None, context: Dict[str, Any] = None) -> MemoryNode:
        """Create a new memory node"""
        node_id = f"mem_{uuid.uuid4()}"
        
        node = MemoryNode(
            id=node_id,
            content=content,
            memory_type=memory_type,
            timestamp=datetime.now(),
            importance=importance,
            tags=tags or [],
            context=context or {},
            retention_score=importance.value / 4.0  # Higher importance = higher retention
        )
        
        return node
    
    def add_node(self, node: MemoryNode):
        """Add a node to the memory web"""
        self.nodes[node.id] = node
        
        # Update indexes
        self.type_index[node.memory_type].append(node.id)
        
        for tag in node.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            if node.id not in self.tag_index[tag]:
                self.tag_index[tag].append(node.id)
        
        # Initialize connections for this node
        if node.id not in self.connections:
            self.connections[node.id] = []
        
        # Update stats
        self.stats["total_nodes"] += 1
        if node.memory_type in [MemoryType.INTERACTION, MemoryType.EMOTIONAL]:
            self.stats["daily_nodes"] += 1
        else:
            self.stats["wisdom_nodes"] += 1
    
    def connect_nodes(self, node1_id: str, node2_id: str, strength: float = 0.5):
        """Create a connection between two nodes"""
        if node1_id in self.nodes and node2_id in self.nodes:
            # Add bidirectional connection
            if node2_id not in self.connections[node1_id]:
                self.connections[node1_id].append(node2_id)
            if node1_id not in self.connections[node2_id]:
                self.connections[node2_id].append(node1_id)
            
            # Update connection strengths
            if node1_id not in self.connection_strengths:
                self.connection_strengths[node1_id] = {}
            if node2_id not in self.connection_strengths:
                self.connection_strengths[node2_id] = {}
            
            self.connection_strengths[node1_id][node2_id] = strength
            self.connection_strengths[node2_id][node1_id] = strength
            
            # Update stats
            self.stats["total_connections"] += 1
    
    def find_related_nodes(self, query: MemoryQuery) -> List[MemoryNode]:
        """Find nodes matching the query"""
        candidates = set()
        
        # Filter by memory types if specified
        if query.memory_types:
            for mem_type in query.memory_types:
                candidates.update(self.type_index.get(mem_type, []))
        else:
            # Include all nodes
            candidates.update(self.nodes.keys())
        
        # Filter by time range if specified
        if query.time_range:
            start_time, end_time = query.time_range
            filtered_candidates = set()
            for node_id in candidates:
                node = self.nodes[node_id]
                if start_time <= node.timestamp <= end_time:
                    filtered_candidates.add(node_id)
            candidates = filtered_candidates
        
        # Filter by tags if specified
        if query.tags:
            tag_matches = set()
            for tag in query.tags:
                if tag in self.tag_index:
                    tag_matches.update(self.tag_index[tag])
            # Intersection: nodes must have ALL specified tags
            candidates = candidates.intersection(tag_matches)
        
        # Filter by importance threshold
        importance_filtered = set()
        for node_id in candidates:
            node = self.nodes[node_id]
            if node.importance.value >= query.importance_threshold.value:
                importance_filtered.add(node_id)
        candidates = importance_filtered
        
        # Apply text search if specified
        if query.text_query:
            text_filtered = set()
            search_terms = query.text_query.lower().split()
            for node_id in candidates:
                node = self.nodes[node_id]
                content_str = str(node.content).lower()
                # Check if any search term is in the content
                if any(term in content_str for term in search_terms):
                    text_filtered.add(node_id)
            candidates = text_filtered
        
        # Convert to list and sort by relevance (importance + recency)
        result_nodes = []
        for node_id in candidates:
            node = self.nodes[node_id]
            # Calculate relevance score based on importance and recency
            time_diff = (datetime.now() - node.timestamp).total_seconds()
            relevance_score = node.importance.value - (time_diff / 86400) * 0.1  # Reduce score for older memories
            result_nodes.append((node, relevance_score))
        
        # Sort by relevance and return top results
        result_nodes.sort(key=lambda x: x[1], reverse=True)
        return [node for node, score in result_nodes[:query.max_results]]
    
    def get_node_connections(self, node_id: str) -> List[MemoryNode]:
        """Get all nodes connected to a specific node"""
        if node_id not in self.connections:
            return []
        
        connected_ids = self.connections[node_id]
        return [self.nodes[nid] for nid in connected_ids if nid in self.nodes]
    
    async def handle_message(self, message: Message):
        """Handle incoming messages"""
        if not self.active:
            return
        
        # Process different types of messages
        if message.content.get("type") == "memory_query":
            query_data = message.content.get("query", {})
            query = MemoryQuery(**query_data) if isinstance(query_data, dict) else MemoryQuery()
            
            results = self.find_related_nodes(query)
            response_msg = Message(
                id=f"{message.id}_response",
                source=self.name,
                destination=message.source,
                content={
                    "type": "memory_results",
                    "results": [node.__dict__ for node in results],
                    "count": len(results)
                },
                context={"response_to": message.id}
            )
            await self.hub.send_message(response_msg)
        
        elif message.content.get("type") == "get_memory_stats":
            # Return current memory statistics
            stats_msg = Message(
                id=f"{message.id}_response",
                source=self.name,
                destination=message.source,
                content={
                    "type": "memory_stats",
                    "stats": self.stats
                },
                context={"response_to": message.id}
            )
            await self.hub.send_message(stats_msg)
    
    async def on_store_memory(self, event_type: str, data: Any):
        """Handle memory storage requests"""
        if data and isinstance(data, dict):
            content = data.get("content")
            memory_type_str = data.get("type", "interaction")
            importance_str = data.get("importance", "normal")
            tags = data.get("tags", [])
            context = data.get("context", {})
            source = data.get("source", "unknown")
            
            # Convert strings to enums
            try:
                memory_type = MemoryType(memory_type_str)
            except ValueError:
                memory_type = MemoryType.INTERACTION
            
            try:
                importance = MemoryImportance(importance_str.upper()) if isinstance(importance_str, str) else MemoryImportance(importance_str)
            except (ValueError, TypeError):
                importance = MemoryImportance.NORMAL
            
            # Create and add the node
            node = self.create_memory_node(content, memory_type, importance, tags, context)
            self.add_node(node)
            
            # Create associative links
            await self.create_associative_links(node)
            
            # Send confirmation
            confirmation_msg = Message(
                id=f"memory_stored_{node.id}",
                source=self.name,
                destination=source,
                content={
                    "type": "memory_stored",
                    "node_id": node.id,
                    "success": True
                }
            )
            await self.hub.send_message(confirmation_msg)
    
    async def on_retrieve_memory(self, event_type: str, data: Any):
        """Handle memory retrieval requests"""
        if data and isinstance(data, dict):
            query_data = data.get("query", {})
            source = data.get("source", "unknown")
            
            query = MemoryQuery(**query_data) if isinstance(query_data, dict) else MemoryQuery()
            results = self.find_related_nodes(query)
            
            response_msg = Message(
                id=f"memory_retrieved_{uuid.uuid4()}",
                source=self.name,
                destination=source,
                content={
                    "type": "memory_retrieved",
                    "results": [node.__dict__ for node in results],
                    "count": len(results),
                    "query": query_data
                }
            )
            await self.hub.send_message(response_msg)
    
    async def on_context_update(self, event_type: str, data: Any):
        """Handle context updates that might affect memory"""
        if data and isinstance(data, dict):
            # Update context in recent memory nodes
            for node_id in list(self.nodes.keys()):
                node = self.nodes[node_id]
                # Update context for recent nodes (last hour)
                if (datetime.now() - node.timestamp).total_seconds() < 3600:
                    node.context.update(data)
    
    async def on_maintenance(self, event_type: str, data: Any):
        """Handle system maintenance tasks"""
        # Perform memory consolidation if needed
        if self.consolidator.should_consolidate():
            # Get daily nodes (interactions and emotional)
            daily_node_ids = (self.type_index.get(MemoryType.INTERACTION, []) + 
                              self.type_index.get(MemoryType.EMOTIONAL, []))
            
            daily_nodes = [self.nodes[nid] for nid in daily_node_ids if nid in self.nodes]
            consolidated_nodes = self.consolidator.consolidate_daily_to_wisdom(daily_nodes)
            
            # Add consolidated nodes
            for node in consolidated_nodes:
                self.add_node(node)
        
        # Perform pruning
        nodes_to_remove = self.pruner.evaluate_for_pruning(list(self.nodes.values()), self.connections)
        for node_id in nodes_to_remove:
            await self.remove_node(node_id)
        
        # Prune weak connections
        self.connections = self.pruner.prune_weak_connections(self.connections, self.connection_strengths)
    
    async def create_associative_links(self, new_node: MemoryNode):
        """Create associative links for a new node"""
        # Find similar nodes to connect to
        all_nodes = list(self.nodes.values())
        
        # Don't include the new node in the search (it's not yet in the main nodes dict properly)
        other_nodes = [node for node in all_nodes if node.id != new_node.id]
        
        similar_node_ids = self.associative_linker.find_similar_nodes(new_node, other_nodes)
        
        for similar_id in similar_node_ids:
            # Calculate connection strength
            similar_node = self.nodes[similar_id]
            strength = self.associative_linker.calculate_similarity(new_node, similar_node)
            
            # Create the connection
            self.connect_nodes(new_node.id, similar_id, strength)
    
    async def remove_node(self, node_id: str):
        """Remove a node and its connections"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            
            # Remove from type index
            if node_id in self.type_index[node.memory_type]:
                self.type_index[node.memory_type].remove(node_id)
            
            # Remove from tag indices
            for tag in node.tags:
                if tag in self.tag_index and node_id in self.tag_index[tag]:
                    self.tag_index[tag].remove(node_id)
            
            # Remove from connections
            if node_id in self.connections:
                connected_nodes = self.connections[node_id]
                for connected_id in connected_nodes:
                    if connected_id in self.connections:
                        if node_id in self.connections[connected_id]:
                            self.connections[connected_id].remove(node_id)
                del self.connections[node_id]
            
            # Remove from main dict
            del self.nodes[node_id]
            
            # Update stats
            self.stats["total_nodes"] -= 1
            if node.memory_type in [MemoryType.INTERACTION, MemoryType.EMOTIONAL]:
                self.stats["daily_nodes"] -= 1
            else:
                self.stats["wisdom_nodes"] -= 1
    
    def get_memory_network_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory network"""
        total_possible_connections = len(self.nodes) * (len(self.nodes) - 1) / 2
        actual_connections = sum(len(conns) for conns in self.connections.values()) // 2  # Divide by 2 for bidirectional
        
        avg_connections_per_node = actual_connections / len(self.nodes) if self.nodes else 0
        
        return {
            "total_nodes": len(self.nodes),
            "total_connections": actual_connections,
            "avg_connections_per_node": avg_connections_per_node,
            "network_density": actual_connections / total_possible_connections if total_possible_connections > 0 else 0,
            "node_distribution": {str(mt): len(ids) for mt, ids in self.type_index.items()},
            "tag_count": len(self.tag_index),
            "latest_node_timestamp": max((node.timestamp for node in self.nodes.values()), default=None),
            "oldest_node_timestamp": min((node.timestamp for node in self.nodes.values()), default=None)
        }
    
    async def update_loop(self):
        """Main update loop for the memory web"""
        while self.active:
            try:
                # Perform maintenance periodically
                if self.consolidator.should_consolidate():
                    await self.hub.trigger_event("system_maintenance", {})
                
                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"Error in memory web update loop: {e}")
                await asyncio.sleep(1)  # Pause on error


# Example usage
async def main():
    # Initialize the core hub
    hub = CoreHub()
    await hub.start()
    
    # Create supporting components
    visual_comp = VisualCompanion(hub)
    voice_synthesizer = VoiceSynthesizer(hub, visual_comp)
    
    # Create the memory web
    memory_web = MemoryWeb(hub, visual_comp, voice_synthesizer)
    
    # Start the update loop in background
    update_task = asyncio.create_task(memory_web.update_loop())
    
    # Simulate storing some memories
    await asyncio.sleep(1)
    
    # Store an identity memory
    identity_msg = Message(
        id="store_identity_1",
        source="identity_module",
        destination="memory_web",
        content={
            "type": "store_memory",
            "content": "I am MIST, a gentle and caring companion",
            "type": "identity",
            "importance": "critical",
            "tags": ["identity", "self", "core"],
            "context": {"source": "self_definition"}
        }
    )
    await hub.send_message(identity_msg)
    
    await asyncio.sleep(1)
    
    # Store an interaction memory
    interaction_msg = Message(
        id="store_interaction_1",
        source="conversation_engine",
        destination="memory_web",
        content={
            "type": "store_memory",
            "content": "User asked about Mars exploration and seemed excited about the possibilities",
            "type": "interaction",
            "importance": "important",
            "tags": ["user_interest", "mars", "exploration"],
            "context": {"user_id": "sister", "topic": "space_exploration"}
        }
    )
    await hub.send_message(interaction_msg)
    
    await asyncio.sleep(1)
    
    # Query for memories about Mars
    query_msg = Message(
        id="query_mars_1",
        source="conversation_engine",
        destination="memory_web",
        content={
            "type": "memory_query",
            "query": {
                "text_query": "mars",
                "max_results": 5
            }
        }
    )
    await hub.send_message(query_msg)
    
    await asyncio.sleep(2)
    
    # Request memory statistics
    stats_msg = Message(
        id="request_stats_1",
        source="debugger",
        destination="memory_web",
        content={
            "type": "get_memory_stats"
        }
    )
    await hub.send_message(stats_msg)
    
    # Let it run for a bit
    await asyncio.sleep(5)
    
    # Cancel the update task and shut down
    update_task.cancel()
    await hub.shutdown()


if __name__ == "__main__":
    # Uncomment to run the example
    # asyncio.run(main())
    pass