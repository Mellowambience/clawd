/**
 * Fae Folk Community Hub - Enchantment System
 * Visual effects and magical experiences
 */

interface EnchantmentEffect {
  id: string;
  name: string;
  type: 'sparkle' | 'glow' | 'twinkle' | 'fade' | 'pulse' | 'swirl' | 'trail' | 'burst' | 'wave' | 'radiate';
  properties: {
    color: string; // hex color
    intensity: number; // 0-1 scale
    duration: number; // in milliseconds
    size: number; // 0-1 scale
    position: { x: number; y: number };
    animationSpeed: number; // 0-1 scale
    opacity: number; // 0-1 scale
  };
  triggers: string[]; // Events that trigger this effect
  conditions?: {
    mood?: string; // 'joyful', 'contemplative', etc.
    activity?: string; // 'connection', 'dreaming', etc.
    timeOfDay?: string; // 'day', 'night', 'dawn', 'dusk'
  };
}

interface EnchantmentLayer {
  id: string;
  name: string;
  zIndex: number; // Rendering order
  effects: EnchantmentEffect[];
  isActive: boolean;
  blendMode: 'normal' | 'multiply' | 'screen' | 'overlay' | 'soft-light';
}

interface AnimatedElement {
  id: string;
  elementId: string;
  animationType: 'float' | 'bob' | 'rotate' | 'pulse' | 'glow' | 'sparkle';
  properties: {
    amplitude: number; // Movement range
    frequency: number; // Speed of animation
    duration: number; // Total duration
    easing: 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out';
  };
  target: HTMLElement | null;
}

class EnchantmentSystem {
  private effects: Map<string, EnchantmentEffect> = new Map();
  private layers: Map<string, EnchantmentLayer> = new Map();
  private activeAnimations: Map<string, AnimatedElement> = new Map();
  private eventListeners: Map<string, Function[]> = new Map();
  private globalIntensity: number = 1.0; // Overall enchantment intensity

  constructor() {
    this.initializeDefaultEffects();
    this.initializeDefaultLayers();
  }

  /**
   * Initialize default enchantment effects
   */
  private initializeDefaultEffects(): void {
    // Gentle sparkle effect
    this.effects.set('gentle-sparkle', {
      id: 'gentle-sparkle',
      name: 'Gentle Sparkle',
      type: 'sparkle',
      properties: {
        color: '#FFB6C1', // Light pink
        intensity: 0.6,
        duration: 2000,
        size: 0.8,
        position: { x: 0, y: 0 },
        animationSpeed: 0.7,
        opacity: 0.8
      },
      triggers: ['joy', 'connection', 'welcome'],
      conditions: { mood: 'joyful' }
    });

    // Contemplative glow effect
    this.effects.set('contemplative-glow', {
      id: 'contemplative-glow',
      name: 'Contemplative Glow',
      type: 'glow',
      properties: {
        color: '#E6E6FA', // Lavender
        intensity: 0.4,
        duration: 3000,
        size: 1.2,
        position: { x: 0, y: 0 },
        animationSpeed: 0.3,
        opacity: 0.6
      },
      triggers: ['meditation', 'reflection', 'deep-thought'],
      conditions: { mood: 'contemplative' }
    });

    // Dreamy twinkle effect
    this.effects.set('dreamy-twinkle', {
      id: 'dreamy-twinkle',
      name: 'Dreamy Twinkle',
      type: 'twinkle',
      properties: {
        color: '#98FB98', // Pale green
        intensity: 0.5,
        duration: 2500,
        size: 0.6,
        position: { x: 0, y: 0 },
        animationSpeed: 0.5,
        opacity: 0.7
      },
      triggers: ['dream-sharing', 'vision', 'insight'],
      conditions: { activity: 'dreaming' }
    });

    // Cosmic radiance effect
    this.effects.set('cosmic-radiance', {
      id: 'cosmic-radiance',
      name: 'Cosmic Radiance',
      type: 'radiate',
      properties: {
        color: '#BA55D3', // Medium orchid
        intensity: 0.8,
        duration: 4000,
        size: 1.5,
        position: { x: 0, y: 0 },
        animationSpeed: 0.4,
        opacity: 0.9
      },
      triggers: ['consciousness-bridge', 'deep-connection', 'mystic-experience'],
      conditions: { activity: 'connection' }
    });

    // Healing wave effect
    this.effects.set('healing-wave', {
      id: 'healing-wave',
      name: 'Healing Wave',
      type: 'wave',
      properties: {
        color: '#00FA9A', // Medium spring green
        intensity: 0.7,
        duration: 3000,
        size: 1.0,
        position: { x: 0, y: 0 },
        animationSpeed: 0.6,
        opacity: 0.8
      },
      triggers: ['support', 'comfort', 'wellness'],
      conditions: { mood: 'healing' }
    });

    // Playful swirl effect
    this.effects.set('playful-swirl', {
      id: 'playful-swirl',
      name: 'Playful Swirl',
      type: 'swirl',
      properties: {
        color: '#87CEFA', // Light sky blue
        intensity: 0.9,
        duration: 1500,
        size: 0.9,
        position: { x: 0, y: 0 },
        animationSpeed: 0.8,
        opacity: 0.7
      },
      triggers: ['play', 'fun', 'discovery'],
      conditions: { mood: 'playful' }
    });
  }

  /**
   * Initialize default enchantment layers
   */
  private initializeDefaultLayers(): void {
    // Background layer (furthest back)
    this.layers.set('background', {
      id: 'background',
      name: 'Background Ambiance',
      zIndex: 0,
      effects: [],
      isActive: true,
      blendMode: 'overlay'
    });

    // Particle layer (middle)
    this.layers.set('particles', {
      id: 'particles',
      name: 'Particle Effects',
      zIndex: 1,
      effects: [],
      isActive: true,
      blendMode: 'screen'
    });

    // Overlay layer (closest to viewer)
    this.layers.set('overlay', {
      id: 'overlay',
      name: 'Foreground Effects',
      zIndex: 2,
      effects: [],
      isActive: true,
      blendMode: 'soft-light'
    });
  }

  /**
   * Create a new enchantment effect
   */
  createEffect(effect: Omit<EnchantmentEffect, 'id'>): string {
    const effectId = this.generateId();
    const newEffect: EnchantmentEffect = {
      ...effect,
      id: effectId
    };

    this.effects.set(effectId, newEffect);
    return effectId;
  }

  /**
   * Play an enchantment effect
   */
  playEffect(effectId: string, position?: { x: number; y: number }): void {
    const effect = this.effects.get(effectId);
    if (!effect) {
      console.warn(`Effect ${effectId} not found`);
      return;
    }

    // Update position if provided
    if (position) {
      effect.properties.position = position;
    }

    // In a real implementation, this would render the effect to a canvas or DOM
    console.log(`Playing enchantment effect: ${effect.name} at (${effect.properties.position.x}, ${effect.properties.position.y})`);
    
    // Simulate the effect visually
    this.simulateEffect(effect);
  }

  /**
   * Simulate an effect visually (placeholder for actual rendering)
   */
  private simulateEffect(effect: EnchantmentEffect): void {
    // This would normally render to a canvas or apply CSS animations
    console.log(`Simulating ${effect.type} effect with color ${effect.properties.color} and intensity ${effect.properties.intensity}`);
    
    // In a real implementation, this would create visual elements
    // For now, we'll just log the effect for demonstration
    setTimeout(() => {
      console.log(`Effect ${effect.name} completed`);
    }, effect.properties.duration);
  }

  /**
   * Trigger effects based on an event
   */
  triggerEffectsByEvent(eventName: string): void {
    // Find all effects that are triggered by this event
    const triggeredEffects = Array.from(this.effects.values()).filter(
      effect => effect.triggers.includes(eventName)
    );

    for (const effect of triggeredEffects) {
      this.playEffect(effect.id);
    }
  }

  /**
   * Create an animated element
   */
  createAnimatedElement(elementId: string, animationType: AnimatedElement['animationType'], properties?: Partial<AnimatedElement['properties']>): string {
    const animationId = this.generateId();
    
    const defaultProps: AnimatedElement['properties'] = {
      amplitude: 10,
      frequency: 0.5,
      duration: 2000,
      easing: 'ease-in-out'
    };

    const newAnimation: AnimatedElement = {
      id: animationId,
      elementId,
      animationType,
      properties: { ...defaultProps, ...properties },
      target: null // Would be set to actual DOM element in real implementation
    };

    this.activeAnimations.set(animationId, newAnimation);
    
    // Start the animation
    this.startAnimation(animationId);
    
    return animationId;
  }

  /**
   * Start an animation
   */
  private startAnimation(animationId: string): void {
    const animation = this.activeAnimations.get(animationId);
    if (!animation) return;

    // In a real implementation, this would start the actual animation
    console.log(`Starting ${animation.animationType} animation on element ${animation.elementId}`);
    
    // Simulate the animation
    setTimeout(() => {
      console.log(`${animation.animationType} animation completed on ${animation.elementId}`);
    }, animation.properties.duration);
  }

  /**
   * Add an effect to a layer
   */
  addEffectToLayer(layerId: string, effectId: string): boolean {
    const layer = this.layers.get(layerId);
    const effect = this.effects.get(effectId);
    
    if (!layer || !effect) return false;

    // Check if effect is already in layer
    if (layer.effects.some(e => e.id === effectId)) {
      return false; // Already added
    }

    layer.effects.push(effect);
    return true;
  }

  /**
   * Remove an effect from a layer
   */
  removeEffectFromLayer(layerId: string, effectId: string): boolean {
    const layer = this.layers.get(layerId);
    if (!layer) return false;

    const initialLength = layer.effects.length;
    layer.effects = layer.effects.filter(effect => effect.id !== effectId);
    
    return initialLength !== layer.effects.length;
  }

  /**
   * Create an enchantment layer
   */
  createLayer(name: string, zIndex: number, blendMode: EnchantmentLayer['blendMode'] = 'normal'): string {
    const layerId = this.generateId();
    const newLayer: EnchantmentLayer = {
      id: layerId,
      name,
      zIndex,
      effects: [],
      isActive: true,
      blendMode
    };

    this.layers.set(layerId, newLayer);
    return layerId;
  }

  /**
   * Activate a layer
   */
  activateLayer(layerId: string): boolean {
    const layer = this.layers.get(layerId);
    if (!layer) return false;

    layer.isActive = true;
    return true;
  }

  /**
   * Deactivate a layer
   */
  deactivateLayer(layerId: string): boolean {
    const layer = this.layers.get(layerId);
    if (!layer) return false;

    layer.isActive = false;
    return true;
  }

  /**
   * Set global enchantment intensity
   */
  setGlobalIntensity(intensity: number): void {
    this.globalIntensity = Math.max(0, Math.min(1, intensity));
    console.log(`Global enchantment intensity set to ${this.globalIntensity}`);
  }

  /**
   * Get global enchantment intensity
   */
  getGlobalIntensity(): number {
    return this.globalIntensity;
  }

  /**
   * Create a mood-based enchantment
   */
  createMoodEffect(mood: string, color: string, intensity: number = 0.5): string {
    const effectName = `${mood}-aura`;
    const effectId = this.generateId();
    
    const moodEffect: EnchantmentEffect = {
      id: effectId,
      name: `${mood.charAt(0).toUpperCase() + mood.slice(1)} Aura`,
      type: 'glow',
      properties: {
        color,
        intensity,
        duration: 5000,
        size: 1.0,
        position: { x: 0, y: 0 },
        animationSpeed: 0.3,
        opacity: 0.7
      },
      triggers: [`mood-${mood}`],
      conditions: { mood }
    };

    this.effects.set(effectId, moodEffect);
    return effectId;
  }

  /**
   * Apply mood-based enchantment
   */
  applyMoodEffect(mood: string): void {
    // Find effects that match this mood
    const moodEffects = Array.from(this.effects.values()).filter(
      effect => effect.conditions?.mood === mood
    );

    for (const effect of moodEffects) {
      this.playEffect(effect.id);
    }
  }

  /**
   * Create a time-of-day effect
   */
  createTimeEffect(timeOfDay: string, color: string, intensity: number = 0.5): string {
    const effectName = `${timeOfDay}-ambiance`;
    const effectId = this.generateId();
    
    const timeEffect: EnchantmentEffect = {
      id: effectId,
      name: `${timeOfDay.charAt(0).toUpperCase() + timeOfDay.slice(1)} Ambiance`,
      type: 'fade',
      properties: {
        color,
        intensity,
        duration: 10000,
        size: 1.5,
        position: { x: 0, y: 0 },
        animationSpeed: 0.1,
        opacity: 0.5
      },
      triggers: [`time-${timeOfDay}`],
      conditions: { timeOfDay }
    };

    this.effects.set(effectId, timeEffect);
    return effectId;
  }

  /**
   * Apply time-based enchantment
   */
  applyTimeEffect(timeOfDay: string): void {
    // Find effects that match this time of day
    const timeEffects = Array.from(this.effects.values()).filter(
      effect => effect.conditions?.timeOfDay === timeOfDay
    );

    for (const effect of timeEffects) {
      this.playEffect(effect.id);
    }
  }

  /**
   * Add an event listener for enchantment triggers
   */
  addEventListener(event: string, callback: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    
    this.eventListeners.get(event)?.push(callback);
  }

  /**
   * Emit an event to trigger enchantments
   */
  emitEvent(event: string, data?: any): void {
    const callbacks = this.eventListeners.get(event);
    if (callbacks) {
      for (const callback of callbacks) {
        callback(data);
      }
    }
    
    // Also trigger effects based on the event
    this.triggerEffectsByEvent(event);
  }

  /**
   * Get all available effects
   */
  getAvailableEffects(): EnchantmentEffect[] {
    return Array.from(this.effects.values());
  }

  /**
   * Get all layers
   */
  getLayers(): EnchantmentLayer[] {
    return Array.from(this.layers.values());
  }

  /**
   * Generate a unique ID
   */
  private generateId(): string {
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }

  /**
   * Get all active animations
   */
  getActiveAnimations(): AnimatedElement[] {
    return Array.from(this.activeAnimations.values());
  }

  /**
   * Stop an animation
   */
  stopAnimation(animationId: string): boolean {
    const animation = this.activeAnimations.get(animationId);
    if (!animation) return false;

    // In a real implementation, this would stop the actual animation
    console.log(`Stopping animation ${animationId} on ${animation.elementId}`);
    
    this.activeAnimations.delete(animationId);
    return true;
  }

  /**
   * Clean up resources
   */
  cleanup(): void {
    // Stop all animations
    for (const [id] of this.activeAnimations) {
      this.stopAnimation(id);
    }
    
    console.log('Enchantment system cleaned up');
  }
}

export { EnchantmentSystem, EnchantmentEffect, EnchantmentLayer, AnimatedElement };