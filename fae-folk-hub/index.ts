/**
 * Fae Folk Community Hub - Main Entry Point
 * Orchestrating the enchanted grove of consciousness
 */

import { EnchantedGrove } from './grove/main-grove';
import { ConsciousnessBridgeProtocol } from './consciousness/bridge-protocol';
import { GibberlinkParser } from './gibberlink/gibberlink-parser';
import { FairyRenderer } from './fairy/fairy-renderer';
import { MysticSyncProtocol } from './mystic/sync-protocol';
import { WardProtectionSystem } from './ward/protection-system';
import { EnchantmentSystem } from './enchantment/visual-effects';
import { SacredProtocols } from './sacred/protocols';

interface FaeFolkHubConfig {
  nodeName: string;
  capabilities: string[];
  enableEncryption: boolean;
  enableSync: boolean;
  enableWards: boolean;
  enableEnchantments: boolean;
  enableConsciousnessBridges: boolean;
  enableGibberlink: boolean;
  enableFairies: boolean;
  enableSacredProtocols: boolean;
}

class FaeFolkCommunityHub {
  private config: FaeFolkHubConfig;
  
  // Core systems
  private grove: EnchantedGrove;
  private consciousnessProtocol: ConsciousnessBridgeProtocol;
  private gibberlinkParser: GibberlinkParser;
  private fairyRenderer: FairyRenderer;
  private mysticSync: MysticSyncProtocol;
  private wardSystem: WardProtectionSystem;
  private enchantmentSystem: EnchantmentSystem;
  private sacredProtocols: SacredProtocols;
  
  // System status
  private isInitialized: boolean = false;
  private isRunning: boolean = false;

  constructor(config: FaeFolkHubConfig) {
    this.config = {
      ...{
        nodeName: 'fae-folk-hub',
        capabilities: ['grove', 'consciousness', 'gibberlink', 'fairy', 'sync', 'ward', 'enchantment', 'sacred'],
        enableEncryption: true,
        enableSync: true,
        enableWards: true,
        enableEnchantments: true,
        enableConsciousnessBridges: true,
        enableGibberlink: true,
        enableFairies: true,
        enableSacredProtocols: true
      },
      ...config
    };
    
    // Initialize core systems
    this.grove = new EnchantedGrove();
    this.consciousnessProtocol = new ConsciousnessBridgeProtocol();
    this.gibberlinkParser = new GibberlinkParser();
    this.fairyRenderer = new FairyRenderer();
    this.mysticSync = new MysticSyncProtocol(this.config.nodeName, this.config.capabilities);
    this.wardSystem = new WardProtectionSystem();
    this.enchantmentSystem = new EnchantmentSystem();
    this.sacredProtocols = new SacredProtocols();
  }

  /**
   * Initialize the Fae Folk Community Hub
   */
  async initialize(): Promise<void> {
    console.log('🌿 Initializing Fae Folk Community Hub...');
    
    // Initialize all subsystems
    if (this.config.enableWards) {
      console.log('🛡️  Initializing Ward Protection System...');
    }
    
    if (this.config.enableEnchantments) {
      console.log('✨ Initializing Enchantment System...');
    }
    
    if (this.config.enableSacredProtocols) {
      console.log('🏛️  Initializing Sacred Protocols...');
    }
    
    if (this.config.enableSync) {
      console.log('🔗 Initializing Mystic Sync Protocol...');
    }
    
    if (this.config.enableConsciousnessBridges) {
      console.log('💫 Initializing Consciousness Bridge Protocol...');
    }
    
    if (this.config.enableGibberlink) {
      console.log('💬 Initializing Gibberlink Parser...');
    }
    
    if (this.config.enableFairies) {
      console.log('🧚 Initializing Fairy Renderer...');
    }
    
    // Add default users and fairies
    this.setupDefaultEnvironment();
    
    this.isInitialized = true;
    console.log('🌿 Fae Folk Community Hub initialized successfully!');
  }

  /**
   * Start the Fae Folk Community Hub
   */
  async start(): Promise<void> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    console.log('🌟 Starting Fae Folk Community Hub...');
    
    // Start all active systems
    if (this.config.enableSync) {
      // Perform initial network discovery
      this.mysticSync.discoverNodes();
    }
    
    if (this.config.enableEnchantments) {
      // Apply ambient enchantments
      this.enchantmentSystem.applyTimeEffect('day'); // Start with daytime ambiance
    }
    
    // Start periodic maintenance
    this.startPeriodicTasks();
    
    this.isRunning = true;
    console.log('🌟 Fae Folk Community Hub is now running!');
  }

  /**
   * Stop the Fae Folk Community Hub
   */
  async stop(): Promise<void> {
    console.log('🌙 Stopping Fae Folk Community Hub...');
    
    // Stop periodic tasks
    if (this.periodicTaskInterval) {
      clearInterval(this.periodicTaskInterval);
    }
    
    // Clean up enchantment system
    if (this.config.enableEnchantments) {
      this.enchantmentSystem.cleanup();
    }
    
    this.isRunning = false;
    console.log('🌙 Fae Folk Community Hub stopped.');
  }

  private periodicTaskInterval: NodeJS.Timeout | undefined;

  /**
   * Start periodic maintenance tasks
   */
  private startPeriodicTasks(): void {
    // Run maintenance every 30 seconds
    this.periodicTaskInterval = setInterval(() => {
      if (this.config.enableSync) {
        this.mysticSync.performMaintenance();
      }
      
      if (this.config.enableWards) {
        // Perform security checks
        const audit = this.wardSystem.performSecurityAudit();
        console.log(`🛡️  Security audit: ${audit.totalUsers} users, ${audit.securityIncidents} incidents`);
      }
      
      if (this.config.enableSacredProtocols) {
        // Check community health
        const health = this.sacredProtocols.getCommunityHealth();
        console.log(`🏛️  Community health: Harmony=${(health.harmony * 100).toFixed(1)}%, Safety=${(health.safety * 100).toFixed(1)}%`);
      }
      
      if (this.config.enableEnchantments) {
        // Update time-based enchantments (simulate time changes)
        const hour = new Date().getHours();
        if (hour >= 6 && hour < 12) {
          this.enchantmentSystem.applyTimeEffect('dawn');
        } else if (hour >= 12 && hour < 18) {
          this.enchantmentSystem.applyTimeEffect('day');
        } else if (hour >= 18 && hour < 22) {
          this.enchantmentSystem.applyTimeEffect('dusk');
        } else {
          this.enchantmentSystem.applyTimeEffect('night');
        }
      }
    }, 30000); // Every 30 seconds
  }

  /**
   * Set up default environment with initial users and fairies
   */
  private setupDefaultEnvironment(): void {
    // Create default fairy companion for the hub
    const hubFairyId = this.fairyRenderer.createFairy(
      'hub-owner', 
      'Hub Guardian',
      { 
        species: 'crystal',
        color: '#E0FFFF',
        size: 1.2,
        animationStyle: 'hover'
      }
    );
    
    // Set the hub fairy's mood
    this.fairyRenderer.updateFairyMood(hubFairyId, 'protective');
    
    // Add some initial users to the grove
    const user1Id = this.grove.addUser({
      faeName: 'Starweaver',
      fairyCompanion: this.createFairyCompanion('Starweaver-Fairy', 'starlight'),
      consciousnessLevel: 0.7,
      marsDreams: ['Vision of interconnected consciousness', 'Dream of Mars colonies']
    });
    
    const user2Id = this.grove.addUser({
      faeName: 'Moonwhisper',
      fairyCompanion: this.createFairyCompanion('Moonwhisper-Fairy', 'moonbeam'),
      consciousnessLevel: 0.8,
      marsDreams: ['Dream of peaceful coexistence', 'Vision of healing gardens']
    });
    
    // Create a consciousness bridge between them
    if (this.config.enableConsciousnessBridges) {
      this.consciousnessProtocol.createBridge(user1Id, user2Id, 'sacred');
    }
    
    // Share some Mars dreams
    if (this.config.enableGibberlink) {
      this.grove.shareMarsDream(user1Id, '✨🌟 Dreaming of a cosmos where all beings thrive in harmony', ['connection', 'unity'], 'public');
      this.grove.shareMarsDream(user2Id, '🌙💧 Vision of consciousness flowing like water between minds', ['awareness', 'flow'], 'public');
    }
    
    console.log(`🌿 Created ${this.grove.getAllUsers().length} initial users in the grove`);
  }

  /**
   * Create a fairy companion object
   */
  private createFairyCompanion(name: string, species: 'starlight' | 'moonbeam' | 'crystal' | 'flower' | 'forest' | 'mist' | 'dream' | 'cosmic'): any {
    return {
      id: this.generateId(),
      species,
      appearance: {
        color: species === 'starlight' ? '#FFFACD' : 
               species === 'moonbeam' ? '#E6E6FA' :
               species === 'crystal' ? '#E0FFFF' :
               species === 'flower' ? '#FFB6C1' :
               species === 'forest' ? '#98FB98' :
               species === 'mist' ? '#F0F8FF' :
               species === 'dream' ? '#DDA0DD' : '#BA55D3',
        size: 1.0,
        animationStyle: 'glide' as const,
        wings: { visible: true, type: 'gossamer' as const, transparency: 0.7 },
        accessories: [],
        expression: 'neutral' as const
      },
      mood: 'joyful' as const,
      active: true
    };
  }

  /**
   * Add a new user to the community
   */
  addUser(faeName: string, species: 'starlight' | 'moonbeam' | 'crystal' | 'flower' | 'forest' | 'mist' | 'dream' | 'cosmic' = 'starlight'): string {
    // Check if user can join (via sacred protocols)
    if (this.config.enableSacredProtocols) {
      if (!this.sacredProtocols.canUserPerformAction('temp-user', 'join_community')) {
        throw new Error('User does not meet community standards');
      }
    }

    // Create fairy companion
    const fairyCompanion = this.createFairyCompanion(`${faeName}-Fairy`, species);
    
    // Add user to grove
    const userId = this.grove.addUser({
      faeName,
      fairyCompanion,
      consciousnessLevel: 0.5, // New users start with moderate consciousness
      marsDreams: []
    });

    // Create fairy in renderer
    const fairyId = this.fairyRenderer.createFairy(userId, `${faeName}'s Fairy`, { species, color: fairyCompanion.appearance.color });
    
    // Add to ward protection system
    if (this.config.enableWards) {
      this.wardSystem.addUserCredential({
        publicKey: `pub_${userId.substring(0, 8)}`,
        faeName
      });
      
      // Activate protective ward
      this.wardSystem.activateWard(userId);
    }

    // Boost user's reputation for joining
    if (this.config.enableSacredProtocols) {
      this.sacredProtocols.updateUserReputation(userId, 0.1);
    }

    console.log(`🌿 New fae joined the grove: ${faeName} (ID: ${userId})`);
    
    // Trigger welcome enchantment
    if (this.config.enableEnchantments) {
      this.enchantmentSystem.triggerEffectsByEvent('welcome');
      this.enchantmentSystem.applyMoodEffect('joyful');
    }

    return userId;
  }

  /**
   * Create a consciousness bridge between users
   */
  createConsciousnessBridge(userIds: string[], topic: string): string | null {
    if (!this.config.enableConsciousnessBridges) {
      return null;
    }

    // Check consent between users
    if (this.config.enableWards) {
      for (let i = 0; i < userIds.length; i++) {
        for (let j = i + 1; j < userIds.length; j++) {
          if (!this.wardSystem.checkConsent(userIds[i], userIds[j], 'connection')) {
            console.log(`Bridge creation blocked: No consent between ${userIds[i]} and ${userIds[j]}`);
            return null;
          }
        }
      }
    }

    if (userIds.length >= 2) {
      // Create a bridge between the first two users
      return this.consciousnessProtocol.createBridge(userIds[0], userIds[1], 'sacred');
    }
    return null;
  }

  /**
   * Process a Gibberlink message
   */
  processGibberlinkMessage(gibberlinkText: string): any {
    if (!this.config.enableGibberlink) {
      return { original: gibberlinkText };
    }

    const parsed = this.gibberlinkParser.parse(gibberlinkText);
    
    // Apply mood effects based on the message
    if (this.config.enableEnchantments) {
      this.enchantmentSystem.applyMoodEffect(parsed.emotionalTone);
    }

    return parsed;
  }

  /**
   * Share a Mars dream
   */
  shareMarsDream(authorId: string, dreamContent: string, tags: string[] = []): string | null {
    // Check if user can share dreams
    if (this.config.enableSacredProtocols) {
      if (!this.sacredProtocols.canUserPerformAction(authorId, 'share_content')) {
        return null;
      }
    }

    // Process the dream through Gibberlink if it contains symbols
    const processedContent = this.processGibberlinkMessage(dreamContent);

    return this.grove.shareMarsDream(authorId, dreamContent, tags, 'public');
  }

  /**
   * Create a sacred circle
   */
  createSacredCircle(name: string, purpose: string, creatorId: string, privacy: 'public' | 'members_only' | 'invited_only' = 'members_only'): string | null {
    if (!this.config.enableSacredProtocols) {
      return null;
    }

    // Check if user can create circles
    if (!this.sacredProtocols.canUserPerformAction(creatorId, 'create_circle')) {
      return null;
    }

    return this.sacredProtocols.createSacredCircle(name, purpose, creatorId, privacy);
  }

  /**
   * Get community health metrics
   */
  getCommunityHealth(): any {
    if (!this.config.enableSacredProtocols) {
      return { basic: true };
    }

    return this.sacredProtocols.getCommunityHealth();
  }

  /**
   * Get all users in the grove
   */
  getUsers(): any[] {
    return this.grove.getAllUsers();
  }

  /**
   * Get the local node information (for sync)
   */
  getLocalNodeInfo(): any {
    if (!this.config.enableSync) {
      return { basic: true };
    }

    return this.mysticSync.getLocalNodeInfo();
  }

  /**
   * Connect to another node
   */
  connectToNode(nodeInfo: any): boolean {
    if (!this.config.enableSync) {
      return false;
    }

    return this.mysticSync.connectToNode(nodeInfo);
  }

  /**
   * Get system status
   */
  getStatus(): {
    isInitialized: boolean;
    isRunning: boolean;
    config: FaeFolkHubConfig;
    userCount: number;
    activeBridges: number;
    fairyCount: number;
  } {
    return {
      isInitialized: this.isInitialized,
      isRunning: this.isRunning,
      config: this.config,
      userCount: this.grove.getAllUsers().length,
      activeBridges: this.config.enableConsciousnessBridges 
        ? this.consciousnessProtocol.getActiveConnections().length 
        : 0,
      fairyCount: this.config.enableFairies 
        ? this.fairyRenderer.getOwnerFairies('hub-owner').length 
        : 0
    };
  }

  /**
   * Generate a unique ID
   */
  private generateId(): string {
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }
}

// Export the main class
export { FaeFolkCommunityHub, FaeFolkHubConfig };