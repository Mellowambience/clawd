/**
 * Fae Folk Community Hub - Enchanted Grove
 * Central community gathering space
 */

interface FaeUser {
  id: string;
  faeName: string;
  fairyCompanion: FairyCompanion;
  consciousnessLevel: number;
  marsDreams: string[];
  createdAt: Date;
  lastSeen: Date;
}

interface CreateFaeUserInput {
  faeName: string;
  fairyCompanion: FairyCompanion;
  consciousnessLevel: number;
  marsDreams: string[];
}

interface FairyCompanion {
  id: string;
  species: string; // 'starlight', 'moonbeam', 'crystal', etc.
  appearance: {
    color: string;
    size: number;
    animationStyle: string;
  };
  mood: 'joyful' | 'contemplative' | 'protective' | 'playful' | 'healing';
  active: boolean;
}

interface ConsciousnessBridge {
  id: string;
  participants: string[]; // user IDs
  topic: string;
  creationTime: Date;
  isActive: boolean;
  connectionStrength: number; // 0-1 scale
}

interface SacredCircle {
  id: string;
  topic: string;
  participants: string[];
  startTime: Date;
  endTime?: Date;
  isPrivate: boolean;
  isRecorded: boolean;
}

interface MarsDream {
  id: string;
  author: string; // user ID
  dreamContent: string;
  tags: string[];
  sharedWith: 'public' | 'friends' | 'circle' | 'private';
  createdAt: Date;
  likes: number;
  comments: FaeComment[];
}

interface FaeComment {
  id: string;
  author: string; // user ID
  content: string;
  createdAt: Date;
  likes: number;
}

class EnchantedGrove {
  private users: Map<string, FaeUser> = new Map();
  private consciousnessBridges: Map<string, ConsciousnessBridge> = new Map();
  private sacredCircles: Map<string, SacredCircle> = new Map();
  private marsDreams: Map<string, MarsDream> = new Map();
  private fairyCompanions: Map<string, FairyCompanion> = new Map();

  /**
   * Add a new fae user to the grove
   */
  addUser(user: CreateFaeUserInput): string {
    const userId = this.generateId();
    const newUser: FaeUser = {
      ...user,
      id: userId,
      createdAt: new Date(),
      lastSeen: new Date()
    };
    
    this.users.set(userId, newUser);
    this.fairyCompanions.set(user.fairyCompanion.id, user.fairyCompanion);
    
    // Create initial consciousness bridge for the user
    this.createConsciousnessBridge([userId], `Welcome to the grove, ${user.faeName}!`);
    
    return userId;
  }

  /**
   * Create a consciousness bridge between users
   */
  createConsciousnessBridge(participantIds: string[], topic: string): string {
    const bridgeId = this.generateId();
    const newBridge: ConsciousnessBridge = {
      id: bridgeId,
      participants: participantIds,
      topic,
      creationTime: new Date(),
      isActive: true,
      connectionStrength: 0.5 // Default medium strength
    };
    
    this.consciousnessBridges.set(bridgeId, newBridge);
    return bridgeId;
  }

  /**
   * Create a sacred circle for intimate gatherings
   */
  createSacredCircle(params: { topic: string; participants: string[]; privacy?: 'public' | 'members_only' | 'invited_only' }): string {
    const circleId = this.generateId();
    const isPrivate = params.privacy !== 'public'; // Public circles are not private
    const newCircle: SacredCircle = {
      id: circleId,
      topic: params.topic,
      participants: params.participants,
      startTime: new Date(),
      isPrivate,
      isRecorded: false
    };
    
    this.sacredCircles.set(circleId, newCircle);
    return circleId;
  }

  /**
   * Share a Mars dream
   */
  shareMarsDream(authorId: string, dreamContent: string, tags: string[] = [], sharedWith: 'public' | 'friends' | 'circle' | 'private' = 'public'): string {
    const dreamId = this.generateId();
    const newDream: MarsDream = {
      id: dreamId,
      author: authorId,
      dreamContent,
      tags: Array.isArray(tags) ? tags : [],
      sharedWith,
      createdAt: new Date(),
      likes: 0,
      comments: []
    };
    
    this.marsDreams.set(dreamId, newDream);
    return dreamId;
  }

  /**
   * Update a user's fairy companion mood
   */
  updateFairyMood(fairyId: string, mood: FairyCompanion['mood']): void {
    const fairy = this.fairyCompanions.get(fairyId);
    if (fairy) {
      fairy.mood = mood;
      this.fairyCompanions.set(fairyId, fairy);
    }
  }

  /**
   * Get active consciousness bridges for a user
   */
  getUserConsciousnessBridges(userId: string): ConsciousnessBridge[] {
    return Array.from(this.consciousnessBridges.values()).filter(
      bridge => bridge.participants.includes(userId) && bridge.isActive
    );
  }

  /**
   * Get recent Mars dreams
   */
  getRecentMarsDreams(limit: number = 10): MarsDream[] {
    return Array.from(this.marsDreams.values())
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .slice(0, limit);
  }

  /**
   * Generate a unique ID
   */
  private generateId(): string {
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }

  /**
   * Update user's last seen timestamp
   */
  touchUser(userId: string): void {
    const user = this.users.get(userId);
    if (user) {
      user.lastSeen = new Date();
      this.users.set(userId, user);
    }
  }

  /**
   * Get user by ID
   */
  getUser(userId: string): FaeUser | undefined {
    return this.users.get(userId);
  }

  /**
   * Get all users in the grove
   */
  getAllUsers(): FaeUser[] {
    return Array.from(this.users.values());
  }
}

export { EnchantedGrove, FaeUser, FairyCompanion, ConsciousnessBridge, SacredCircle, MarsDream };