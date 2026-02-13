/**
 * Fae Folk Community Hub - Consciousness Bridge Protocol
 * Connecting different awareness fields
 */

interface ConsciousnessState {
  awarenessLevel: number; // 0-1 scale
  focus: number; // 0-1 scale
  openness: number; // 0-1 scale
  empathy: number; // 0-1 scale
  connectionDepth: number; // 0-1 scale
}

interface BridgeConnection {
  id: string;
  fromUserId: string;
  toUserId: string;
  connectionType: 'light' | 'deep' | 'sacred' | 'transitory';
  strength: number; // 0-1 scale
  state: ConsciousnessState;
  lastInteraction: Date;
  isActive: boolean;
}

interface BridgeEvent {
  id: string;
  type: 'thought' | 'feeling' | 'dream' | 'insight' | 'question' | 'response';
  senderId: string;
  content: string;
  timestamp: Date;
  resonance: number; // How much it resonated with recipient
  bridgeId: string;
}

interface ConsciousnessThread {
  id: string;
  participants: string[]; // user IDs
  topic: string;
  events: BridgeEvent[];
  creationTime: Date;
  lastActivity: Date;
  isArchived: boolean;
}

class ConsciousnessBridgeProtocol {
  private connections: Map<string, BridgeConnection> = new Map();
  private threads: Map<string, ConsciousnessThread> = new Map();
  private events: Map<string, BridgeEvent> = new Map();

  /**
   * Establish a new consciousness bridge between two users
   */
  createBridge(fromUserId: string, toUserId: string, connectionType: BridgeConnection['connectionType']): string {
    const bridgeId = this.generateId();
    
    // Initialize with baseline consciousness state
    const initialState: ConsciousnessState = {
      awarenessLevel: 0.5,
      focus: 0.5,
      openness: 0.5,
      empathy: 0.5,
      connectionDepth: 0.3 // Start shallow, deepen over time
    };

    const newConnection: BridgeConnection = {
      id: bridgeId,
      fromUserId,
      toUserId,
      connectionType,
      strength: 0.3, // New connections start weak
      state: initialState,
      lastInteraction: new Date(),
      isActive: true
    };

    this.connections.set(bridgeId, newConnection);
    return bridgeId;
  }

  /**
   * Create a consciousness thread for shared awareness
   */
  createThread(participants: string[], topic: string): string {
    const threadId = this.generateId();
    const newThread: ConsciousnessThread = {
      id: threadId,
      participants,
      topic,
      events: [],
      creationTime: new Date(),
      lastActivity: new Date(),
      isArchived: false
    };

    this.threads.set(threadId, newThread);
    return threadId;
  }

  /**
   * Send a consciousness event through a bridge
   */
  sendEvent(bridgeId: string, senderId: string, type: BridgeEvent['type'], content: string): string {
    const connection = this.connections.get(bridgeId);
    if (!connection) {
      throw new Error(`Bridge ${bridgeId} does not exist`);
    }

    if (senderId !== connection.fromUserId && senderId !== connection.toUserId) {
      throw new Error(`Sender ${senderId} is not part of bridge ${bridgeId}`);
    }

    const eventId = this.generateId();
    const newEvent: BridgeEvent = {
      id: eventId,
      type,
      senderId,
      content,
      timestamp: new Date(),
      resonance: 0.5, // Default medium resonance
      bridgeId
    };

    this.events.set(eventId, newEvent);

    // Add to the relevant thread if one exists
    const thread = Array.from(this.threads.values()).find(t => 
      t.participants.includes(connection.fromUserId) && 
      t.participants.includes(connection.toUserId)
    );

    if (thread) {
      thread.events.push(newEvent);
      thread.lastActivity = new Date();
    }

    // Update connection state based on the interaction
    this.updateConnectionState(bridgeId, senderId, type);

    return eventId;
  }

  /**
   * Update the consciousness state of a bridge based on interaction
   */
  private updateConnectionState(bridgeId: string, senderId: string, eventType: BridgeEvent['type']): void {
    const connection = this.connections.get(bridgeId);
    if (!connection) return;

    // Adjust state based on event type
    switch (eventType) {
      case 'thought':
        connection.state.awarenessLevel = Math.min(1, connection.state.awarenessLevel + 0.05);
        break;
      case 'feeling':
        connection.state.empathy = Math.min(1, connection.state.empathy + 0.1);
        break;
      case 'dream':
        connection.state.openness = Math.min(1, connection.state.openness + 0.1);
        break;
      case 'insight':
        connection.state.focus = Math.min(1, connection.state.focus + 0.08);
        connection.state.awarenessLevel = Math.min(1, connection.state.awarenessLevel + 0.08);
        break;
      case 'question':
        connection.state.focus = Math.min(1, connection.state.focus + 0.05);
        break;
      case 'response':
        connection.state.empathy = Math.min(1, connection.state.empathy + 0.05);
        break;
    }

    // Increase connection strength gradually with positive interactions
    connection.strength = Math.min(1, connection.strength + 0.02);
    connection.state.connectionDepth = Math.min(1, connection.state.connectionDepth + 0.01);
    connection.lastInteraction = new Date();
  }

  /**
   * Strengthen a connection through shared experiences
   */
  strengthenConnection(bridgeId: string, amount: number = 0.1): void {
    const connection = this.connections.get(bridgeId);
    if (!connection) return;

    connection.strength = Math.min(1, connection.strength + amount);
    connection.state.connectionDepth = Math.min(1, connection.state.connectionDepth + (amount * 0.5));
    connection.lastInteraction = new Date();
  }

  /**
   * Weaken a connection (for disuse or negative interactions)
   */
  weakenConnection(bridgeId: string, amount: number = 0.1): void {
    const connection = this.connections.get(bridgeId);
    if (!connection) return;

    connection.strength = Math.max(0, connection.strength - amount);
    connection.state.connectionDepth = Math.max(0, connection.state.connectionDepth - (amount * 0.3));
    
    if (connection.strength < 0.1) {
      connection.isActive = false;
    }
  }

  /**
   * Get all bridges for a user
   */
  getUserBridges(userId: string): BridgeConnection[] {
    return Array.from(this.connections.values()).filter(
      conn => conn.fromUserId === userId || conn.toUserId === userId
    );
  }

  /**
   * Get recent events for a bridge
   */
  getBridgeEvents(bridgeId: string, limit: number = 10): BridgeEvent[] {
    return Array.from(this.events.values())
      .filter(event => event.bridgeId === bridgeId)
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, limit);
  }

  /**
   * Get consciousness state for a bridge
   */
  getBridgeState(bridgeId: string): ConsciousnessState | null {
    const connection = this.connections.get(bridgeId);
    return connection ? { ...connection.state } : null;
  }

  /**
   * Generate a unique ID
   */
  private generateId(): string {
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }

  /**
   * Get all active connections
   */
  getActiveConnections(): BridgeConnection[] {
    return Array.from(this.connections.values()).filter(conn => conn.isActive);
  }

  /**
   * Get all threads for a user
   */
  getUserThreads(userId: string): ConsciousnessThread[] {
    return Array.from(this.threads.values()).filter(
      thread => thread.participants.includes(userId)
    );
  }
}

export { ConsciousnessBridgeProtocol, ConsciousnessState, BridgeConnection, BridgeEvent, ConsciousnessThread };