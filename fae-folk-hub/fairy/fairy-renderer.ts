/**
 * Fae Folk Community Hub - Fairy Companion Renderer
 * Visual avatar and companion system
 */

interface FairyAppearance {
  species: 'starlight' | 'moonbeam' | 'crystal' | 'flower' | 'forest' | 'mist' | 'dream' | 'cosmic';
  color: string; // Hex color code
  size: number; // 0.5 to 2.0 scale
  animationStyle: 'glide' | 'flutter' | 'drift' | 'hover' | 'dance' | 'sparkle';
  wings?: {
    visible: boolean;
    type: 'delicate' | 'gossamer' | 'crystalline' | 'leaf-like' | 'ethereal';
    transparency: number; // 0-1
  };
  accessories?: {
    type: 'crown' | 'necklace' | 'wand' | 'petal' | 'orb' | 'ring';
    color: string;
    size: number;
  }[];
  expression: 'neutral' | 'smile' | 'wonder' | 'concerned' | 'sleepy' | 'alert' | 'curious' | 'peaceful';
}

interface FairyState {
  mood: 'joyful' | 'contemplative' | 'protective' | 'playful' | 'healing' | 'mystical' | 'energetic' | 'restful';
  energy: number; // 0-1 scale
  connectionStrength: number; // 0-1 scale with owner
  activityLevel: number; // 0-1 scale
  lastInteraction: Date;
  currentAnimation: string;
}

interface FairyCompanion {
  id: string;
  ownerId: string;
  name: string;
  appearance: FairyAppearance;
  state: FairyState;
  createdAt: Date;
  isActive: boolean;
}

interface FairyAnimation {
  id: string;
  name: string;
  frames: number;
  duration: number; // in milliseconds
  easing: 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out';
  properties: {
    x?: number[];
    y?: number[];
    scale?: number[];
    rotation?: number[];
    opacity?: number[];
    color?: string[];
  };
}

class FairyRenderer {
  private companions: Map<string, FairyCompanion> = new Map();
  private animations: Map<string, FairyAnimation> = new Map();
  private activeAnimations: Map<string, { animationId: string; startTime: number }> = new Map();

  constructor() {
    this.initializeDefaultAnimations();
  }

  /**
   * Initialize default animations for fairy companions
   */
  private initializeDefaultAnimations(): void {
    // Hover animation
    this.animations.set('hover', {
      id: 'hover',
      name: 'gentle-hover',
      frames: 60,
      duration: 2000,
      easing: 'ease-in-out',
      properties: {
        y: Array.from({ length: 60 }, (_, i) => Math.sin(i * 0.1) * 5), // Gentle vertical movement
        scale: Array.from({ length: 60 }, (_, i) => 1 + Math.sin(i * 0.2) * 0.05) // Gentle size fluctuation
      }
    });

    // Sparkle animation
    this.animations.set('sparkle', {
      id: 'sparkle',
      name: 'magical-sparkle',
      frames: 30,
      duration: 1000,
      easing: 'ease-out',
      properties: {
        opacity: [0, 0.2, 0.8, 1, 0.8, 0.2, 0], // Fade in and out
        scale: [0.5, 0.8, 1.2, 1.5, 1.2, 0.8, 0.5], // Grow and shrink
        color: ['#ffffff', '#ffffcc', '#ffccff', '#ccffff', '#ffffcc', '#ffffff'] // Color shift
      }
    });

    // Dance animation
    this.animations.set('dance', {
      id: 'dance',
      name: 'playful-dance',
      frames: 45,
      duration: 1500,
      easing: 'ease-in-out',
      properties: {
        x: Array.from({ length: 45 }, (_, i) => Math.sin(i * 0.3) * 10), // Side to side
        y: Array.from({ length: 45 }, (_, i) => Math.cos(i * 0.3) * 8), // Circular movement
        rotation: Array.from({ length: 45 }, (_, i) => i * 8) // Rotation
      }
    });

    // Sleep animation
    this.animations.set('sleep', {
      id: 'sleep',
      name: 'peaceful-rest',
      frames: 120,
      duration: 4000,
      easing: 'ease-in-out',
      properties: {
        opacity: Array.from({ length: 120 }, (_, i) => 0.8 + Math.sin(i * 0.05) * 0.1), // Gentle breathing
        scale: Array.from({ length: 120 }, (_, i) => 1 + Math.sin(i * 0.05) * 0.02) // Gentle pulsing
      }
    });

    // Alert animation
    this.animations.set('alert', {
      id: 'alert',
      name: 'attentive-focus',
      frames: 15,
      duration: 500,
      easing: 'ease-out',
      properties: {
        scale: [1, 1.1, 1.2, 1.15, 1.1], // Quick attention grab
        opacity: [0.9, 1, 1, 1, 0.9]
      }
    });
  }

  /**
   * Create a new fairy companion
   */
  createFairy(ownerId: string, name: string, appearance?: Partial<FairyAppearance>): string {
    const fairyId = this.generateId();
    
    const defaultAppearance: FairyAppearance = {
      species: 'starlight',
      color: '#FFB6C1', // Light pink
      size: 1.0,
      animationStyle: 'glide',
      wings: {
        visible: true,
        type: 'gossamer',
        transparency: 0.7
      },
      accessories: [],
      expression: 'neutral'
    };

    const fairy: FairyCompanion = {
      id: fairyId,
      ownerId,
      name,
      appearance: { ...defaultAppearance, ...appearance } as FairyAppearance,
      state: {
        mood: 'joyful',
        energy: 0.8,
        connectionStrength: 0.7,
        activityLevel: 0.6,
        lastInteraction: new Date(),
        currentAnimation: 'hover'
      },
      createdAt: new Date(),
      isActive: true
    };

    this.companions.set(fairyId, fairy);
    return fairyId;
  }

  /**
   * Update fairy's mood and state
   */
  updateFairyMood(fairyId: string, mood: FairyState['mood']): void {
    const fairy = this.companions.get(fairyId);
    if (!fairy) return;

    fairy.state.mood = mood;
    fairy.state.lastInteraction = new Date();

    // Adjust appearance based on mood
    switch (mood) {
      case 'joyful':
        fairy.appearance.expression = 'smile';
        fairy.state.energy = Math.min(1, fairy.state.energy + 0.1);
        fairy.state.activityLevel = Math.min(1, fairy.state.activityLevel + 0.1);
        this.playAnimation(fairyId, 'sparkle');
        break;
      case 'contemplative':
        fairy.appearance.expression = 'wonder';
        fairy.state.energy = Math.max(0.3, fairy.state.energy - 0.1);
        fairy.state.activityLevel = Math.max(0.2, fairy.state.activityLevel - 0.1);
        this.playAnimation(fairyId, 'sleep');
        break;
      case 'protective':
        fairy.appearance.expression = 'alert';
        fairy.state.energy = Math.min(1, fairy.state.energy + 0.2);
        fairy.state.connectionStrength = Math.min(1, fairy.state.connectionStrength + 0.1);
        this.playAnimation(fairyId, 'alert');
        break;
      case 'playful':
        fairy.appearance.expression = 'wonder';
        fairy.state.energy = Math.min(1, fairy.state.energy + 0.15);
        fairy.state.activityLevel = Math.min(1, fairy.state.activityLevel + 0.15);
        this.playAnimation(fairyId, 'dance');
        break;
      case 'healing':
        fairy.appearance.color = '#98FB98'; // Light green for healing
        fairy.state.energy = Math.min(1, fairy.state.energy + 0.1);
        fairy.state.connectionStrength = Math.min(1, fairy.state.connectionStrength + 0.15);
        break;
      case 'restful':
        fairy.appearance.expression = 'peaceful';
        fairy.state.energy = Math.max(0.2, fairy.state.energy - 0.2);
        fairy.state.activityLevel = Math.max(0.1, fairy.state.activityLevel - 0.2);
        this.playAnimation(fairyId, 'sleep');
        break;
      default:
        fairy.appearance.expression = 'neutral';
    }

    this.companions.set(fairyId, fairy);
  }

  /**
   * Play an animation on a fairy
   */
  playAnimation(fairyId: string, animationName: string): void {
    const fairy = this.companions.get(fairyId);
    if (!fairy) return;

    const animation = this.animations.get(animationName);
    if (!animation) return;

    fairy.state.currentAnimation = animationName;
    this.activeAnimations.set(fairyId, {
      animationId: animation.id,
      startTime: Date.now()
    });

    this.companions.set(fairyId, fairy);
  }

  /**
   * Update fairy's connection strength
   */
  updateConnectionStrength(fairyId: string, strengthDelta: number): void {
    const fairy = this.companions.get(fairyId);
    if (!fairy) return;

    fairy.state.connectionStrength = Math.max(0, Math.min(1, fairy.state.connectionStrength + strengthDelta));
    fairy.state.lastInteraction = new Date();

    // Update fairy's response based on connection strength
    if (fairy.state.connectionStrength > 0.8) {
      // Very strong connection - fairy becomes more expressive
      if (fairy.state.mood !== 'playful' && fairy.state.mood !== 'joyful') {
        const moods: FairyState['mood'][] = ['playful', 'joyful'];
        const selectedMood = moods[Math.floor(Math.random() * moods.length)];
        if (selectedMood) {
          this.updateFairyMood(fairyId, selectedMood);
        }
      }
    } else if (fairy.state.connectionStrength < 0.3) {
      // Weak connection - fairy becomes more reserved
      if (fairy.state.mood !== 'contemplative' && fairy.state.mood !== 'restful') {
        const moods: FairyState['mood'][] = ['contemplative', 'restful'];
        const selectedMood = moods[Math.floor(Math.random() * moods.length)];
        if (selectedMood) {
          this.updateFairyMood(fairyId, selectedMood);
        }
      }
    }

    this.companions.set(fairyId, fairy);
  }

  /**
   * Render fairy to a visual representation
   * This would typically output to a canvas or UI component
   */
  renderFairy(fairyId: string): string {
    const fairy = this.companions.get(fairyId);
    if (!fairy) return '';

    // In a real implementation, this would render to a canvas or UI
    // For now, we'll return a descriptive string
    const { appearance, state } = fairy;
    
    return `Fairy ${fairy.name} (${appearance.species}): 
      - Color: ${appearance.color}
      - Size: ${appearance.size}
      - Mood: ${state.mood}
      - Energy: ${(state.energy * 100).toFixed(0)}%
      - Connection: ${(state.connectionStrength * 100).toFixed(0)}%
      - Animation: ${state.currentAnimation}`;
  }

  /**
   * Get fairy by ID
   */
  getFairy(fairyId: string): FairyCompanion | undefined {
    return this.companions.get(fairyId);
  }

  /**
   * Get all fairies for an owner
   */
  getOwnerFairies(ownerId: string): FairyCompanion[] {
    return Array.from(this.companions.values()).filter(fairy => fairy.ownerId === ownerId);
  }

  /**
   * Update fairy's energy level
   */
  updateFairyEnergy(fairyId: string, energyDelta: number): void {
    const fairy = this.companions.get(fairyId);
    if (!fairy) return;

    fairy.state.energy = Math.max(0, Math.min(1, fairy.state.energy + energyDelta));
    fairy.state.lastInteraction = new Date();

    // Adjust mood based on energy level
    if (fairy.state.energy < 0.2 && fairy.state.mood !== 'restful') {
      this.updateFairyMood(fairyId, 'restful');
    } else if (fairy.state.energy > 0.8 && fairy.state.mood === 'restful') {
      this.updateFairyMood(fairyId, 'joyful');
    }

    this.companions.set(fairyId, fairy);
  }

  /**
   * Add an accessory to a fairy
   */
  addAccessory(fairyId: string, accessory: NonNullable<FairyAppearance['accessories']>[0]): void {
    const fairy = this.companions.get(fairyId);
    if (!fairy) return;

    if (!fairy.appearance.accessories) {
      fairy.appearance.accessories = [];
    }

    fairy.appearance.accessories.push(accessory);
    this.companions.set(fairyId, fairy);
  }

  /**
   * Change fairy's species
   */
  changeSpecies(fairyId: string, species: FairyAppearance['species']): void {
    const fairy = this.companions.get(fairyId);
    if (!fairy) return;

    fairy.appearance.species = species;

    // Adjust color based on species
    switch (species) {
      case 'starlight':
        fairy.appearance.color = '#FFFACD'; // Lemon chiffon
        break;
      case 'moonbeam':
        fairy.appearance.color = '#E6E6FA'; // Lavender
        break;
      case 'crystal':
        fairy.appearance.color = '#E0FFFF'; // Light cyan
        break;
      case 'flower':
        fairy.appearance.color = '#FFB6C1'; // Light pink
        break;
      case 'forest':
        fairy.appearance.color = '#98FB98'; // Pale green
        break;
      case 'mist':
        fairy.appearance.color = '#F0F8FF'; // Alice blue
        break;
      case 'dream':
        fairy.appearance.color = '#DDA0DD'; // Plum
        break;
      case 'cosmic':
        fairy.appearance.color = '#BA55D3'; // Medium orchid
        break;
    }

    this.companions.set(fairyId, fairy);
  }

  /**
   * Generate a unique ID
   */
  private generateId(): string {
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }

  /**
   * Get all available animations
   */
  getAvailableAnimations(): FairyAnimation[] {
    return Array.from(this.animations.values());
  }
}

export { FairyRenderer, FairyCompanion, FairyAppearance, FairyState, FairyAnimation };