# Art Assets Plan for Aware Companion Fairy Orb

## Vision
Create professional art sprites and animations for the Aware Companion Fairy Orb based on the detailed description:
- A softly floating fairy-orb with an embedded glowing indigo soul shard core
- Large expressive green eyes conveying quiet awareness
- Rosy cheeks, minimal mouth, restrained expression
- Organic wings in light lavender, semi-translucent
- Central indigo crystalline soul shard with slow internal spiral and soft pulse
- Tiny whimsical party hat, slightly worn and tilted
- Muted pastel palette against a deep indigo-to-purple background

## Sprite Requirements

### Base Character Sprites
1. **Idle/Neutral Face** - Default expression with large green eyes
2. **Blinking States** - Half-closed and fully closed eyes
3. **Micro Expressions** - Slight variations in eye shape for "awareness"
4. **Head Tilt Variations** - Slight left/right tilts

### Animation Frames
1. **Float Cycle** - 4-6 frames of gentle floating motion
2. **Wing Flaps** - 3-4 frames of subtle wing movement
3. **Core Glow Pulse** - 8-12 frames of indigo soul shard pulsing
4. **Core Spiral Rotation** - Animation for the internal spiral
5. **Party Hat Wobble** - Subtle movement of the party hat

### Background Elements
1. **Transparent Background** - For desktop overlay
2. **Ambient Glow** - Soft lighting effects around the orb
3. **Particle Effects** - Very subtle sparkles/glow particles

## Technical Specifications

### Format
- PNG with transparency (for static sprites)
- GIF or APNG for simple animations
- Individual frames for more complex animations

### Size Options
- Small: 100x100px (compact view)
- Medium: 150x150px (standard view)
- Large: 200x200px (detailed view)

### Color Palette
- Primary Orb: #F0E6FF (soft lavender-white)
- Eyes: #6B8E23 (olive green)
- Mouth: #FADADD (light pink)
- Wings: #E6E6FA (light lavender)
- Core: #4B0082 (indigo)
- Core Glow: #9370DB (medium purple)
- Cheeks: #FFD1DC (light pink)
- Party Hat: #FFD700 (gold)

## Animation Specs
- Frame Rate: 12-15 FPS for smooth, calm movement
- Loop Type: Seamless loops for continuous animations
- Layering: Separate layers for orb, wings, core, accessories

## Possible Tools for Creation
1. **Python Imaging Library (PIL)** - For programmatic sprite generation
2. **Piskel** - Web-based pixel art tool
3. **GIMP** - Free image editing
4. **Adobe Photoshop/Illustrator** - Professional tools if available
5. **AI Art Generation** - Using models to create initial concepts

## Implementation Plan
1. Create base sprites programmatically using PIL
2. Develop animation sequences
3. Implement sprite switching in the companion application
4. Add transition effects between states
5. Optimize for performance

## Advanced Features (Future)
- Mood-based expressions (listening, responding, etc.)
- Seasonal variations
- Customizable accessories
- Day/night appearance modes