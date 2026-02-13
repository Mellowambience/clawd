"""
Sprite Sheet Generator for Aware Companion Fairy Orb
Following exact specifications for production-ready sprite sheet
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os


def create_fairy_orb_frame(y_offset=0, wing_flap=0):
    """Create a single frame of the fairy orb with specified offsets"""
    size = (200, 200)
    img = Image.new('RGBA', size, (255, 255, 255, 0))  # Transparent background
    draw = ImageDraw.Draw(img)
    
    # Calculate center and orb radius with vertical offset
    center_x, center_y = size[0] // 2, size[1] // 2
    orb_radius = 60
    
    # Apply vertical offset (limited to 5% of height as specified)
    max_offset = int(size[1] * 0.05)  # 5% of height
    adjusted_y = center_y + int(y_offset * max_offset)
    
    # Draw the orb body (soft lavender-white)
    draw.ellipse([
        center_x - orb_radius, 
        adjusted_y - orb_radius, 
        center_x + orb_radius, 
        adjusted_y + orb_radius
    ], fill=(240, 230, 255, 255), outline=(224, 208, 240, 255), width=1)
    
    # Add subtle texture (hand-crafted feel)
    for i in range(8):
        angle = (i * 45) * math.pi / 180
        x = center_x + (orb_radius - 10) * math.cos(angle)
        y = adjusted_y + (orb_radius - 10) * math.sin(angle)
        draw.ellipse([x-1, y-1, x+1, y+1], fill=(230, 230, 250, 255))
    
    # Draw rosy cheeks
    draw.ellipse([
        center_x - 35, adjusted_y + 5,
        center_x - 25, adjusted_y + 11
    ], fill=(255, 209, 220, 150))  # Light pink with transparency
    
    draw.ellipse([
        center_x + 25, adjusted_y + 5,
        center_x + 35, adjusted_y + 11
    ], fill=(255, 209, 220, 150))  # Light pink with transparency
    
    # Draw large expressive green eyes (quiet awareness)
    left_eye_x, right_eye_x = center_x - 20, center_x + 20
    eye_y = adjusted_y - 5
    eye_size = 10
    
    # Draw open eyes with soft expression
    # Left eye
    draw.ellipse([
        left_eye_x - eye_size, eye_y - eye_size,
        left_eye_x + eye_size, eye_y + eye_size
    ], fill=(255, 255, 255, 255), outline=(208, 208, 208, 255), width=1)
    
    # Right eye
    draw.ellipse([
        right_eye_x - eye_size, eye_y - eye_size,
        right_eye_x + eye_size, eye_y + eye_size
    ], fill=(255, 255, 255, 255), outline=(208, 208, 208, 255), width=1)
    
    # Draw olive green irises
    iris_size = eye_size * 0.6
    draw.ellipse([
        left_eye_x - iris_size, eye_y - iris_size,
        left_eye_x + iris_size, eye_y + iris_size
    ], fill=(107, 142, 35, 255))  # Olive green
    
    draw.ellipse([
        right_eye_x - iris_size, eye_y - iris_size,
        right_eye_x + iris_size, eye_y + iris_size
    ], fill=(107, 142, 35, 255))  # Olive green
    
    # Draw pupils
    draw.ellipse([
        left_eye_x - 3, eye_y - 2,
        left_eye_x + 1, eye_y + 1
    ], fill=(47, 47, 47, 255))
    
    draw.ellipse([
        right_eye_x - 3, eye_y - 2,
        right_eye_x + 1, eye_y + 1
    ], fill=(47, 47, 47, 255))
    
    # Draw subtle eye highlights
    draw.ellipse([
        left_eye_x - 1, eye_y - 1,
        left_eye_x, eye_y
    ], fill=(240, 240, 240, 255))
    
    draw.ellipse([
        right_eye_x - 1, eye_y - 1,
        right_eye_x, eye_y
    ], fill=(240, 240, 240, 255))
    
    # Draw minimal mouth (restrained expression)
    mouth_y = adjusted_y + 20
    mouth_width = 12
    mouth_height = 6
    draw.arc([
        center_x - mouth_width//2, 
        mouth_y - mouth_height//4,
        center_x + mouth_width//2, 
        mouth_y + mouth_height//4
    ], start=10, end=170, fill=(250, 218, 221, 255), width=1)  # Light pink
    
    # Draw the indigo soul shard core (glowing, faceted)
    core_x = center_x
    core_y = adjusted_y
    
    # Core glow (soft, not flashy)
    core_size = 15
    glow_size = core_size + 3
    draw.ellipse([
        core_x - glow_size, core_y - glow_size,
        core_x + glow_size, core_y + glow_size
    ], fill=(147, 112, 219, 100))  # Medium purple with transparency
    
    # Draw faceted soul shard
    core_points = []
    for i in range(8):
        angle = (i * 45) * math.pi / 180  # No rotation for consistency
        radius = core_size * (0.8 + 0.2 * math.sin(i * 0.7))
        px = core_x + radius * math.cos(angle)
        py = core_y + radius * math.sin(angle)
        core_points.extend([px, py])
    
    draw.polygon(core_points, fill=(75, 0, 130, 255), outline=(122, 92, 148, 255), width=1)  # Indigo
    
    # Draw internal spiral of the soul shard (static for consistency)
    spiral_points = []
    for i in range(20):
        angle = (i * 18) * math.pi / 180  # Static rotation for consistency
        radius = core_size * 0.6 * (1 - i/20)
        px = core_x + radius * math.cos(angle)
        py = core_y + radius * math.sin(angle)
        spiral_points.extend([int(px), int(py)])
    
    if len(spiral_points) >= 4:
        draw.line(spiral_points, fill=(177, 156, 217, 200), width=1, joint="curve")
    
    # Draw organic wings (light lavender, semi-translucent) with micro-twitch
    wing_offset = wing_flap * 2  # Limited wing movement as specified
    
    # Left wing points
    left_wing_points = [
        (center_x - 60, adjusted_y - 20 + wing_offset),  # Wing tip with micro-twitch
        (center_x - 75, adjusted_y - 30),               # Upper attachment
        (center_x - 65, adjusted_y),                     # Lower attachment
        (center_x - 55, adjusted_y - 5)                  # Wing base
    ]
    draw.polygon(left_wing_points, fill=(230, 230, 250, 180))  # Light lavender with transparency
    
    # Right wing points
    right_wing_points = [
        (center_x + 60, adjusted_y - 20 - wing_offset),  # Wing tip with opposite micro-twitch
        (center_x + 75, adjusted_y - 30),               # Upper attachment
        (center_x + 65, adjusted_y),                     # Lower attachment
        (center_x + 55, adjusted_y - 5)                  # Wing base
    ]
    draw.polygon(right_wing_points, fill=(230, 230, 250, 180))  # Light lavender with transparency
    
    # Draw tiny whimsical party hat (slightly worn, tilted)
    hat_x, hat_y = center_x + 5, adjusted_y - 25
    hat_points = [
        (hat_x, hat_y - 15),      # Tip of hat
        (hat_x - 8, hat_y - 5),   # Left base
        (hat_x + 8, hat_y - 5)    # Right base
    ]
    draw.polygon(hat_points, fill=(255, 215, 0, 255), outline=(212, 175, 55, 255), width=1)  # Gold
    
    # Draw hat decoration
    draw.ellipse([
        hat_x - 2, hat_y - 12, hat_x + 2, hat_y - 8
    ], fill=(255, 105, 180, 255))  # Pink
    
    return img


def generate_sprite_sheet():
    """Generate the complete sprite sheet with 8 frames in a 4x2 grid"""
    # Define the vertical positions for each frame (based on the progression)
    # Frame progression: neutral -> up -> highest -> return center -> down -> lowest -> return center -> neutral
    y_offsets = [0, 0.3, 0.5, 0.3, -0.3, -0.5, -0.3, 0]  # 8 frames
    
    # Wing flap values for micro-twitch (very subtle)
    wing_flaps = [0, 0.1, 0, -0.1, 0, 0.1, 0, -0.1]  # Subtle wing movement
    
    # Create individual frames
    frames = []
    for i in range(8):
        frame = create_fairy_orb_frame(y_offsets[i], wing_flaps[i])
        frames.append(frame)
    
    # Create sprite sheet (4x2 grid: 4 columns, 2 rows)
    sheet_width = 200 * 4  # 4 frames horizontally
    sheet_height = 200 * 2  # 2 rows vertically
    sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (255, 255, 255, 0))
    
    # Paste frames into the sprite sheet
    for row in range(2):  # 2 rows
        for col in range(4):  # 4 columns
            frame_index = row * 4 + col
            if frame_index < len(frames):
                sprite_sheet.paste(frames[frame_index], (col * 200, row * 200))
    
    return sprite_sheet, frames


def save_production_assets():
    """Save the sprite sheet and individual frames"""
    # Create output directory
    os.makedirs("production_sprites", exist_ok=True)
    
    print("Generating sprite sheet with 8 frames in 4x2 grid...")
    
    # Generate the sprite sheet and individual frames
    sprite_sheet, frames = generate_sprite_sheet()
    
    # Save the complete sprite sheet
    sprite_sheet.save("production_sprites/sprite_sheet_aware_companion.png")
    print(f"Saved sprite sheet: 8 frames in 4x2 grid (1600x400px)")
    
    # Save individual frames for verification
    for i, frame in enumerate(frames):
        frame.save(f"production_sprites/frame_{i:02d}.png")
    
    # Create and save a sample animation GIF
    frames[0].save(
        "production_sprites/sample_loop_animation.gif",
        save_all=True,
        append_images=frames[1:],
        duration=150,  # 150ms per frame (6.67 FPS for smooth idle)
        loop=0  # Infinite loop
    )
    
    print("\nProduction assets created in 'production_sprites' directory:")
    print("- sprite_sheet_aware_companion.png (4x2 grid with 8 frames)")
    print("- Individual frames 00-07 for verification")
    print("- sample_loop_animation.gif (seamless loop)")
    print("\nSprite sheet specifications:")
    print("- Orthographic, straight-on view")
    print("- Centered with identical framing")
    print("- Transparent background")
    print("- Clean edges, no background elements")
    print("- 8 frames: Neutral -> Up -> Highest -> Return -> Down -> Lowest -> Return -> Neutral")
    print("- Vertical movement only (<=5% height change)")
    print("- Wings with micro-twitch only")
    print("- Calm, aware, emotionally present expression")
    print("- Consistent proportions, colors, and silhouette")


def main():
    print("Starting Production Sprite Sheet Generator for Aware Companion Fairy Orb...")
    print("Following exact specifications for production-ready assets.")
    
    save_production_assets()
    
    print("\nSprite sheet generation complete!")


if __name__ == "__main__":
    main()