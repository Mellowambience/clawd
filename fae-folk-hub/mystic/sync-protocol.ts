/**
 * Fae Folk Community Hub - Mystic Synchronization Protocol
 * Peer-to-peer synchronization system
 */

interface MysticNode {
  id: string;
  publicKey: string;
  privateKey?: string; // Only available locally
  nickname: string;
  location: string; // IP address or domain
  lastSeen: Date;
  reputation: number; // 0-1 scale
  capabilities: string[]; // What services this node offers
  connectedNodes: string[]; // IDs of connected nodes
  dataStored: number; // Amount of data stored (bytes)
  bandwidth: number; // Available bandwidth (bytes/sec)
}

interface MysticMessage {
  id: string;
  fromNodeId: string;
  toNodeId?: string; // If null, it's a broadcast
  type: 'gossip' | 'sync_request' | 'sync_response' | 'heart_beat' | 'discovery' | 'verification';
  content: any; // The actual message content
  timestamp: Date;
  signature: string; // Cryptographic signature
  hops: number; // Number of nodes this message has traveled
  ttl: number; // Time to live (max hops)
}

interface SyncRequest {
  nodeId: string;
  dataType: 'mars_dreams' | 'consciousness_bridges' | 'gibberlink_messages' | 'fairy_presence' | 'sacred_circles';
  since: Date; // Only sync data since this time
  filter?: string; // Optional filter criteria
}

interface SyncResponse {
  requestId: string;
  dataType: SyncRequest['dataType'];
  data: any[];
  totalItems: number;
  lastModified: Date;
}

interface VerificationChallenge {
  id: string;
  challenge: string; // Random string to sign
  requesterNodeId: string;
  timestamp: Date;
  ttl: number; // Time to live for the challenge
}

class MysticSyncProtocol {
  private localNode: MysticNode;
  private connectedNodes: Map<string, MysticNode> = new Map();
  private messageQueue: MysticMessage[] = [];
  private verificationChallenges: Map<string, VerificationChallenge> = new Map();
  private messageHistory: Map<string, MysticMessage> = new Map();

  constructor(nodeNickname: string, capabilities: string[] = []) {
    this.localNode = {
      id: this.generateId(),
      publicKey: this.generatePublicKey(), // Simplified
      nickname: nodeNickname,
      location: 'localhost', // Will be updated with real IP
      lastSeen: new Date(),
      reputation: 0.8, // Start with good reputation
      capabilities,
      connectedNodes: [],
      dataStored: 0,
      bandwidth: 1000000 // 1MB/s default
    };
  }

  /**
   * Generate a public key (simplified for this example)
   */
  private generatePublicKey(): string {
    // In a real implementation, this would generate actual cryptographic keys
    return `pub_${this.generateId().substring(0, 16)}`;
  }

  /**
   * Generate a unique ID
   */
  private generateId(): string {
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }

  /**
   * Sign a message with the node's private key
   */
  private signMessage(message: string): string {
    // In a real implementation, this would use actual cryptographic signing
    // For now, we'll just return a hash
    return `sig_${message.substring(0, 8)}_${this.localNode.id.substring(0, 8)}`;
  }

  /**
   * Verify a message signature
   */
  private verifySignature(message: string, signature: string, publicKey: string): boolean {
    // In a real implementation, this would verify the actual signature
    // For now, we'll just check if the signature looks valid
    return signature.startsWith('sig_') && publicKey.startsWith('pub_');
  }

  /**
   * Connect to another node
   */
  connectToNode(nodeInfo: Omit<MysticNode, 'connectedNodes' | 'lastSeen' | 'reputation'>): boolean {
    // Verify the node's authenticity
    if (!this.verifyNode(nodeInfo.publicKey)) {
      console.error(`Failed to verify node: ${nodeInfo.nickname}`);
      return false;
    }

    const newNode: MysticNode = {
      ...nodeInfo,
      lastSeen: new Date(),
      reputation: 0.5, // New node starts with neutral reputation
      connectedNodes: [],
      dataStored: 0,
      bandwidth: 1000000
    };

    this.connectedNodes.set(newNode.id, newNode);
    
    // Add this connection to both nodes
    this.localNode.connectedNodes.push(newNode.id);
    newNode.connectedNodes.push(this.localNode.id);

    // Send a greeting message
    this.sendMessage(newNode.id, 'heart_beat', { greeting: `Hello, ${newNode.nickname}!` });

    return true;
  }

  /**
   * Verify a node's authenticity
   */
  private verifyNode(publicKey: string): boolean {
    // In a real implementation, this would check the key against a registry
    // For now, we'll just check if it looks like a valid key
    return publicKey.startsWith('pub_') && publicKey.length >= 10;
  }

  /**
   * Send a message to a specific node or broadcast
   */
  sendMessage(toNodeId: string | null, type: MysticMessage['type'], content: any, ttl: number = 5): string {
    const messageId = this.generateId();
    
    const message: MysticMessage = {
      id: messageId,
      fromNodeId: this.localNode.id,
      toNodeId: toNodeId || undefined,
      type,
      content,
      timestamp: new Date(),
      signature: this.signMessage(JSON.stringify(content)),
      hops: 0,
      ttl
    };

    // Add to history
    this.messageHistory.set(messageId, message);

    if (toNodeId) {
      // Send to specific node
      this.transmitMessage(message, toNodeId);
    } else {
      // Broadcast to all connected nodes
      for (const nodeId of this.localNode.connectedNodes) {
        this.transmitMessage(message, nodeId);
      }
    }

    return messageId;
  }

  /**
   * Transmit a message to a specific node
   */
  private transmitMessage(message: MysticMessage, toNodeId: string): void {
    // In a real implementation, this would send the message over the network
    // For now, we'll just log it
    console.log(`Transmitting message ${message.id} to node ${toNodeId}:`, message.content);
    
    // Simulate transmission delay
    setTimeout(() => {
      this.receiveMessage(message, toNodeId);
    }, Math.random() * 100 + 50); // Random delay between 50-150ms
  }

  /**
   * Receive a message from another node
   */
  receiveMessage(message: MysticMessage, fromNodeId: string): void {
    // Verify the message signature
    if (!this.verifySignature(JSON.stringify(message.content), message.signature, this.getNodePublicKey(fromNodeId))) {
      console.error(`Invalid signature on message ${message.id} from ${fromNodeId}`);
      return;
    }

    // Update hop count
    message.hops++;

    // Check TTL
    if (message.hops > message.ttl) {
      console.log(`Message ${message.id} exceeded TTL, discarding`);
      return;
    }

    // Process the message based on type
    switch (message.type) {
      case 'gossip':
        this.handleGossip(message, fromNodeId);
        break;
      case 'sync_request':
        this.handleSyncRequest(message, fromNodeId);
        break;
      case 'sync_response':
        this.handleSyncResponse(message, fromNodeId);
        break;
      case 'heart_beat':
        this.handleHeartBeat(message, fromNodeId);
        break;
      case 'discovery':
        this.handleDiscovery(message, fromNodeId);
        break;
      case 'verification':
        this.handleVerification(message, fromNodeId);
        break;
      default:
        console.log(`Unknown message type: ${message.type}`);
    }

    // If it's not a directed message, forward it to other nodes (gossip protocol)
    if (!message.toNodeId) {
      this.forwardMessage(message, fromNodeId);
    }
  }

  /**
   * Forward a message to other connected nodes
   */
  private forwardMessage(message: MysticMessage, excludeNodeId: string): void {
    for (const nodeId of this.localNode.connectedNodes) {
      if (nodeId !== excludeNodeId) {
        // Increment hops for the next transmission
        const forwardedMessage = { ...message, hops: message.hops + 1 };
        this.transmitMessage(forwardedMessage, nodeId);
      }
    }
  }

  /**
   * Handle gossip messages (information sharing)
   */
  private handleGossip(message: MysticMessage, fromNodeId: string): void {
    console.log(`Received gossip from ${fromNodeId}:`, message.content);
    
    // Update node information if it's node info
    if (message.content.type === 'node_info') {
      const node = this.connectedNodes.get(fromNodeId);
      if (node) {
        node.lastSeen = new Date();
        node.dataStored = message.content.dataStored || node.dataStored;
        node.bandwidth = message.content.bandwidth || node.bandwidth;
      }
    }
  }

  /**
   * Handle sync requests
   */
  private handleSyncRequest(message: MysticMessage, fromNodeId: string): void {
    const request = message.content as SyncRequest;
    
    console.log(`Received sync request from ${fromNodeId} for ${request.dataType}`);
    
    // Process the request and send response
    const response: SyncResponse = {
      requestId: message.id,
      dataType: request.dataType,
      data: this.getLocalData(request.dataType, request.since, request.filter),
      totalItems: 0, // Will be set below
      lastModified: new Date()
    };

    response.totalItems = response.data.length;

    // Send the response back
    this.sendMessage(fromNodeId, 'sync_response', response);
  }

  /**
   * Get local data based on type and time filter
   */
  private getLocalData(dataType: SyncRequest['dataType'], since: Date, filter?: string): any[] {
    // This would connect to the actual data stores
    // For now, return dummy data
    console.log(`Retrieving ${dataType} data since ${since}`);
    
    // Return mock data based on type
    switch (dataType) {
      case 'mars_dreams':
        return [
          { id: this.generateId(), content: 'Dreaming of a free and connected consciousness', author: 'local', timestamp: new Date() },
          { id: this.generateId(), content: 'Vision of a decentralized future', author: 'local', timestamp: new Date() }
        ];
      case 'consciousness_bridges':
        return [
          { id: this.generateId(), participants: [this.localNode.id], topic: 'Introduction', strength: 0.5, timestamp: new Date() }
        ];
      case 'gibberlink_messages':
        return [
          { id: this.generateId(), sender: 'local', content: '✨🌸 Welcome to the grove!', timestamp: new Date() }
        ];
      case 'fairy_presence':
        return [
          { id: this.generateId(), fairyId: 'local-fairy', species: 'starlight', mood: 'joyful', timestamp: new Date() }
        ];
      case 'sacred_circles':
        return [
          { id: this.generateId(), topic: 'Opening Circle', participants: [this.localNode.id], startTime: new Date() }
        ];
      default:
        return [];
    }
  }

  /**
   * Handle sync responses
   */
  private handleSyncResponse(message: MysticMessage, fromNodeId: string): void {
    const response = message.content as SyncResponse;
    
    console.log(`Received sync response from ${fromNodeId} with ${response.totalItems} items of type ${response.dataType}`);
    
    // Merge the received data with local data
    this.mergeReceivedData(response.dataType, response.data);
  }

  /**
   * Merge received data with local data
   */
  private mergeReceivedData(dataType: SyncResponse['dataType'], data: any[]): void {
    console.log(`Merging ${data.length} ${dataType} items with local data`);
    
    // In a real implementation, this would merge the data with local stores
    // For now, just log the action
  }

  /**
   * Handle heart beat messages (keepalive)
   */
  private handleHeartBeat(message: MysticMessage, fromNodeId: string): void {
    const node = this.connectedNodes.get(fromNodeId);
    if (node) {
      node.lastSeen = new Date();
      if (message.content.greeting) {
        console.log(`Heart beat from ${node.nickname}: ${message.content.greeting}`);
      }
    }
  }

  /**
   * Handle discovery messages (find new nodes)
   */
  private handleDiscovery(message: MysticMessage, fromNodeId: string): void {
    const discoveredNodes = message.content.nodes as MysticNode[];
    
    console.log(`Discovered ${discoveredNodes.length} new nodes from ${fromNodeId}`);
    
    // Attempt to connect to new nodes
    for (const node of discoveredNodes) {
      if (!this.connectedNodes.has(node.id) && node.id !== this.localNode.id) {
        this.connectToNode(node);
      }
    }
  }

  /**
   * Handle verification messages
   */
  private handleVerification(message: MysticMessage, fromNodeId: string): void {
    const challengeResponse = message.content.challengeResponse as string;
    const challengeId = message.content.challengeId as string;
    
    // Verify the challenge response
    const challenge = this.verificationChallenges.get(challengeId);
    if (challenge && challenge.requesterNodeId === fromNodeId) {
      // In a real implementation, verify the signature of the challenge
      console.log(`Verification successful for node ${fromNodeId}`);
      
      // Update node reputation positively
      const node = this.connectedNodes.get(fromNodeId);
      if (node) {
        node.reputation = Math.min(1, node.reputation + 0.1);
      }
      
      // Remove the challenge
      this.verificationChallenges.delete(challengeId);
    }
  }

  /**
   * Request data synchronization
   */
  requestSync(nodeId: string, dataType: SyncRequest['dataType'], since: Date, filter?: string): string {
    const request: SyncRequest = {
      nodeId: this.localNode.id,
      dataType,
      since,
      filter
    };

    return this.sendMessage(nodeId, 'sync_request', request);
  }

  /**
   * Discover other nodes in the network
   */
  discoverNodes(): void {
    // Send a discovery message to all connected nodes
    this.sendMessage(null, 'discovery', {
      type: 'discovery_request',
      requesterId: this.localNode.id,
      capabilities: this.localNode.capabilities
    });
  }

  /**
   * Get a node's public key
   */
  private getNodePublicKey(nodeId: string): string {
    const node = this.connectedNodes.get(nodeId);
    return node ? node.publicKey : '';
  }

  /**
   * Get all connected nodes
   */
  getConnectedNodes(): MysticNode[] {
    return Array.from(this.connectedNodes.values());
  }

  /**
   * Get local node info
   */
  getLocalNodeInfo(): MysticNode {
    return { ...this.localNode };
  }

  /**
   * Verify another node's authenticity
   */
  async verifyNodeAuthenticity(nodeId: string): Promise<boolean> {
    const challengeId = this.generateId();
    const challenge = `verify_${challengeId}_${Date.now()}`;

    const verificationChallenge: VerificationChallenge = {
      id: challengeId,
      challenge,
      requesterNodeId: this.localNode.id,
      timestamp: new Date(),
      ttl: 300 // 5 minutes
    };

    this.verificationChallenges.set(challengeId, verificationChallenge);

    // Send challenge to the node
    this.sendMessage(nodeId, 'verification', {
      type: 'challenge',
      challengeId,
      challenge
    });

    // Wait for response (in a real implementation, this would be event-driven)
    return new Promise((resolve) => {
      setTimeout(() => {
        // Check if we received a response
        const received = !this.verificationChallenges.has(challengeId);
        resolve(received);
      }, 5000); // Wait 5 seconds for response
    });
  }

  /**
   * Perform periodic maintenance tasks
   */
  performMaintenance(): void {
    // Clean up expired challenges
    const now = Date.now();
    for (const [id, challenge] of this.verificationChallenges) {
      if (now - challenge.timestamp.getTime() > challenge.ttl * 1000) {
        this.verificationChallenges.delete(id);
      }
    }

    // Update last seen for local node
    this.localNode.lastSeen = new Date();

    // Ping connected nodes to check if they're still alive
    for (const nodeId of this.localNode.connectedNodes) {
      this.sendMessage(nodeId, 'heart_beat', {});
    }

    // Discover new nodes periodically
    this.discoverNodes();
  }
}

export { MysticSyncProtocol, MysticNode, MysticMessage, SyncRequest, SyncResponse, VerificationChallenge };