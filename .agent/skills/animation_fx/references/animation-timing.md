# Animation Timing Reference

## Easing Functions
- `cubic-bezier(0.165, 0.84, 0.44, 1)`: Clean, decelerating slide.
- `ease-in-out`: Natural breath rhythms.

## Optimization
- Use `requestAnimationFrame` for all Three.js updates.
- Decouple logic from rendering where possible.
- Use `delta` time for consistent speed across different refresh rates.
