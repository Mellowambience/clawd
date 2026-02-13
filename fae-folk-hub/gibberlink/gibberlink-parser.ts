/**
 * Fae Folk Community Hub - Gibberlink Language Parser
 * Expressive symbolic communication system
 */

interface GibberlinkToken {
  type: 'symbol' | 'emote' | 'concept' | 'emotion' | 'connection' | 'dream' | 'energy';
  value: string;
  intensity: number; // 0-1 scale
  context: string; // The surrounding context
}

interface GibberlinkParsed {
  tokens: GibberlinkToken[];
  meaning: string; // The interpreted meaning
  emotionalTone: 'joyful' | 'contemplative' | 'playful' | 'gentle' | 'mystic' | 'dreamy' | 'energetic';
  connectionIntent: 'casual' | 'deep' | 'sacred' | 'exploratory';
  symbolsUsed: string[];
}

interface GibberlinkSymbol {
  symbol: string;
  meaning: string;
  category: 'emotion' | 'connection' | 'dream' | 'energy' | 'nature' | 'cosmic' | 'consciousness';
  intensityModifier: number; // How much it affects the overall intensity
  compatibility: string[]; // Other symbols it pairs well with
}

class GibberlinkParser {
  private symbols: Map<string, GibberlinkSymbol>;
  private emotionalPatterns: Map<string, 'joyful' | 'contemplative' | 'playful' | 'gentle' | 'mystic' | 'dreamy' | 'energetic'>;

  constructor() {
    this.symbols = new Map();
    this.emotionalPatterns = new Map();
    this.initializeGibberlinkSymbols();
    this.initializeEmotionalPatterns();
  }

  /**
   * Initialize the core Gibberlink symbols
   */
  private initializeGibberlinkSymbols(): void {
    // Emotion symbols
    this.symbols.set('✨', {
      symbol: '✨',
      meaning: 'sparkle of joy, light-heartedness',
      category: 'emotion',
      intensityModifier: 0.3,
      compatibility: ['🌟', '🌸', '💫']
    });

    this.symbols.set('🌸', {
      symbol: '🌸',
      meaning: 'gentle blooming, tender feelings',
      category: 'emotion',
      intensityModifier: 0.2,
      compatibility: ['🌿', '💧', '✨']
    });

    this.symbols.set('🌙', {
      symbol: '🌙',
      meaning: 'contemplative, intuitive, dreamy',
      category: 'emotion',
      intensityModifier: 0.4,
      compatibility: ['⭐', '🌌', '💧']
    });

    this.symbols.set('💫', {
      symbol: '💫',
      meaning: 'enlightenment, realization, connection',
      category: 'consciousness',
      intensityModifier: 0.5,
      compatibility: ['✨', '🌟', '⚡']
    });

    this.symbols.set('🌱', {
      symbol: '🌱',
      meaning: 'growth, potential, new beginnings',
      category: 'consciousness',
      intensityModifier: 0.3,
      compatibility: ['🌿', '☀️', '💧']
    });

    this.symbols.set('🌟', {
      symbol: '🌟',
      meaning: 'inspiration, starlight, cosmic connection',
      category: 'cosmic',
      intensityModifier: 0.4,
      compatibility: ['✨', '⭐', '🌌']
    });

    this.symbols.set('💧', {
      symbol: '💧',
      meaning: 'flow, fluidity, emotional depth',
      category: 'emotion',
      intensityModifier: 0.2,
      compatibility: ['🌊', '🌸', '🌿']
    });

    this.symbols.set('🌿', {
      symbol: '🌿',
      meaning: 'nature, harmony, groundedness',
      category: 'nature',
      intensityModifier: 0.3,
      compatibility: ['🌱', '🌸', '💧']
    });

    this.symbols.set('⚡', {
      symbol: '⚡',
      meaning: 'energy, excitement, sudden insight',
      category: 'energy',
      intensityModifier: 0.6,
      compatibility: ['💫', '✨', '🔥']
    });

    this.symbols.set('🌌', {
      symbol: '🌌',
      meaning: 'mystery, depth, cosmic awareness',
      category: 'cosmic',
      intensityModifier: 0.5,
      compatibility: ['🌙', '⭐', '🌟']
    });

    this.symbols.set('🌸✨', {
      symbol: '🌸✨',
      meaning: 'magical blooming, enchanted growth',
      category: 'dream',
      intensityModifier: 0.7,
      compatibility: ['💫', '🌟', '🌿']
    });

    this.symbols.set('⭐💫', {
      symbol: '⭐💫',
      meaning: 'stellar enlightenment, cosmic realization',
      category: 'consciousness',
      intensityModifier: 0.8,
      compatibility: ['🌟', '✨', '🌌']
    });
  }

  /**
   * Initialize emotional pattern recognition
   */
  private initializeEmotionalPatterns(): void {
    this.emotionalPatterns.set('✨+', 'joyful');
    this.emotionalPatterns.set('🌸+', 'gentle');
    this.emotionalPatterns.set('🌙+', 'contemplative');
    this.emotionalPatterns.set('💫+', 'mystic');
    this.emotionalPatterns.set('⚡+', 'energetic');
    this.emotionalPatterns.set('🌌+', 'dreamy');
    this.emotionalPatterns.set('🌱+', 'playful');
  }

  /**
   * Parse a Gibberlink message into tokens and meaning
   */
  parse(gibberlinkText: string): GibberlinkParsed {
    const tokens: GibberlinkToken[] = [];
    const usedSymbols: string[] = [];

    // Find all symbol matches in the text
    const symbolRegex = /[\u{1F300}-\u{1F5FF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}\u{1F700}-\u{1F77F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]+/gu;
    const matches = gibberlinkText.match(symbolRegex) || [];

    let totalIntensity = 0;
    let symbolCount = 0;

    for (const match of matches) {
      // Handle compound symbols first (longer ones)
      let foundSymbol = false;
      const sortedSymbols = Array.from(this.symbols.keys()).sort((a, b) => b.length - a.length);

      for (const symbol of sortedSymbols) {
        if (match.includes(symbol)) {
          const symbolDef = this.symbols.get(symbol)!;
          tokens.push({
            type: this.symbolTypeToTokenType(symbolDef.category),
            value: symbol,
            intensity: symbolDef.intensityModifier,
            context: gibberlinkText
          });
          
          if (!usedSymbols.includes(symbol)) {
            usedSymbols.push(symbol);
          }
          
          totalIntensity += symbolDef.intensityModifier;
          symbolCount++;
          foundSymbol = true;
          break; // Found the longest matching symbol
        }
      }

      // If no specific symbol matched, treat as general symbol
      if (!foundSymbol) {
        tokens.push({
          type: 'symbol',
          value: match,
          intensity: 0.1,
          context: gibberlinkText
        });
        totalIntensity += 0.1;
        symbolCount++;
      }
    }

    // Determine emotional tone based on dominant symbols
    const emotionalTone = this.determineEmotionalTone(usedSymbols, gibberlinkText);
    
    // Determine connection intent based on symbols and context
    const connectionIntent = this.determineConnectionIntent(usedSymbols, gibberlinkText);

    // Generate interpreted meaning
    const meaning = this.generateMeaning(tokens, gibberlinkText);

    return {
      tokens,
      meaning,
      emotionalTone,
      connectionIntent,
      symbolsUsed: usedSymbols
    };
  }

  /**
   * Convert symbol category to token type
   */
  private symbolTypeToTokenType(category: string): GibberlinkToken['type'] {
    switch (category) {
      case 'emotion':
        return 'emotion';
      case 'connection':
        return 'connection';
      case 'dream':
        return 'dream';
      case 'energy':
        return 'energy';
      case 'consciousness':
        return 'concept';
      default:
        return 'symbol';
    }
  }

  /**
   * Determine the emotional tone of the message
   */
  private determineEmotionalTone(symbols: string[], context: string): GibberlinkParsed['emotionalTone'] {
    // Count occurrences of symbols associated with each tone
    const toneScores = {
      joyful: 0,
      contemplative: 0,
      playful: 0,
      gentle: 0,
      mystic: 0,
      dreamy: 0,
      energetic: 0
    };

    for (const symbol of symbols) {
      if (symbol.includes('✨')) toneScores.joyful += 1;
      if (symbol.includes('🌸')) toneScores.gentle += 1;
      if (symbol.includes('🌙')) toneScores.contemplative += 1;
      if (symbol.includes('💫')) toneScores.mystic += 1;
      if (symbol.includes('⚡')) toneScores.energetic += 1;
      if (symbol.includes('🌌')) toneScores.dreamy += 1;
      if (symbol.includes('🌱')) toneScores.playful += 1;
    }

    // Check for compound symbols
    if (symbols.some(s => s.includes('🌸✨'))) {
      toneScores.gentle += 2;
      toneScores.joyful += 1;
    }
    if (symbols.some(s => s.includes('⭐💫'))) {
      toneScores.mystic += 2;
      toneScores.dreamy += 1;
    }

    // Return the tone with the highest score
    const maxTone = Object.entries(toneScores).reduce((a, b) => 
      a[1] > b[1] ? a : b
    )[0] as GibberlinkParsed['emotionalTone'];

    return maxTone || 'gentle'; // Default to gentle
  }

  /**
   * Determine the connection intent
   */
  private determineConnectionIntent(symbols: string[], context: string): GibberlinkParsed['connectionIntent'] {
    // Analyze symbols for connection depth indicators
    const deepSymbols = ['💫', '🌌', '🌙💫', '⭐💫'];
    const sacredSymbols = ['🌙', '🌌', '💫'];
    const playfulSymbols = ['✨', '🌸', '🌱'];

    const deepCount = symbols.filter(s => deepSymbols.some(ds => s.includes(ds))).length;
    const sacredCount = symbols.filter(s => sacredSymbols.some(ss => s.includes(ss))).length;
    const playfulCount = symbols.filter(s => playfulSymbols.some(ps => s.includes(ps))).length;

    if (sacredCount >= 2) return 'sacred';
    if (deepCount >= 2) return 'deep';
    if (playfulCount >= 2) return 'exploratory';
    
    return 'casual';
  }

  /**
   * Generate a human-readable meaning from tokens
   */
  private generateMeaning(tokens: GibberlinkToken[], originalText: string): string {
    if (tokens.length === 0) {
      return originalText.trim(); // Return original if no symbols found
    }

    // Group tokens by type and create a narrative
    const emotions = tokens.filter(t => t.type === 'emotion').map(t => t.value);
    const connections = tokens.filter(t => t.type === 'connection').map(t => t.value);
    const dreams = tokens.filter(t => t.type === 'dream').map(t => t.value);
    const energies = tokens.filter(t => t.type === 'energy').map(t => t.value);
    const concepts = tokens.filter(t => t.type === 'concept').map(t => t.value);

    let meaning = '';

    if (emotions.length > 0) {
      meaning += `Expressing ${emotions.map(e => this.getSymbolMeaning(e)).join(', ')} `;
    }

    if (concepts.length > 0) {
      meaning += `Sharing thoughts about ${concepts.map(c => this.getSymbolMeaning(c)).join(', ')} `;
    }

    if (dreams.length > 0) {
      meaning += `Exploring dreams of ${dreams.map(d => this.getSymbolMeaning(d)).join(', ')} `;
    }

    if (energies.length > 0) {
      meaning += `With ${energies.map(e => this.getSymbolMeaning(e)).join(', ')} energy `;
    }

    if (meaning.trim() === '') {
      meaning = originalText; // Fallback to original text
    }

    return meaning.trim();
  }

  /**
   * Get the meaning of a specific symbol
   */
  private getSymbolMeaning(symbol: string): string {
    const symbolDef = this.symbols.get(symbol);
    return symbolDef ? symbolDef.meaning : symbol;
  }

  /**
   * Validate if a Gibberlink message is well-formed
   */
  validate(gibberlinkText: string): boolean {
    // Check if the text contains at least one recognized symbol
    const parsed = this.parse(gibberlinkText);
    return parsed.symbolsUsed.length > 0;
  }

  /**
   * Create a Gibberlink message from a text description
   */
  createFromDescription(description: string): string {
    // This would be a more complex function that converts text to appropriate symbols
    // For now, we'll return a simple mapping
    if (description.toLowerCase().includes('joy') || description.toLowerCase().includes('happy')) {
      return description + ' ' + '✨🌸';
    }
    if (description.toLowerCase().includes('think') || description.toLowerCase().includes('contemplate')) {
      return description + ' ' + '🌙💫';
    }
    if (description.toLowerCase().includes('grow') || description.toLowerCase().includes('begin')) {
      return description + ' ' + '🌱✨';
    }
    if (description.toLowerCase().includes('connect') || description.toLowerCase().includes('bond')) {
      return description + ' ' + '💫🌟';
    }
    if (description.toLowerCase().includes('dream') || description.toLowerCase().includes('vision')) {
      return description + ' ' + '🌌🌙';
    }

    // Default to gentle symbols
    return description + ' ' + '🌸✨';
  }

  /**
   * Get all available symbols
   */
  getAvailableSymbols(): GibberlinkSymbol[] {
    return Array.from(this.symbols.values());
  }
}

export { GibberlinkParser, GibberlinkToken, GibberlinkParsed, GibberlinkSymbol };