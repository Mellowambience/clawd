"""
Sprite Generator for Aware Companion Fairy Orb
Creates art sprites and animations for the companion
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os


def create_base_orb_sprite(size=(200, 200)):
    """Create the base fairy orb sprite"""
    img = Image.new('RGBA', size, (255, 255, 255, 0))  # Transparent background
    draw = ImageDraw.Draw(img)
    
    # Calculate center and orb radius
    center_x, center_y = size[0] // 2, size[1] // 2
    orb_radius = 60
    
    # Draw the orb body (soft lavender-white)
    draw.ellipse([
        center_x - orb_radius, 
        center_y - orb_radius, 
        center_x + orb_radius, 
        center_y + orb_radius
    ], fill=(240, 230, 255, 255), outline=(224, 208, 240, 255), width=1)
    
    # Add subtle texture (hand-crafted feel)
    for i in range(8):
        angle = (i * 45) * math.pi / 180
        x = center_x + (orb_radius - 10) * math.cos(angle)
        y = center_y + (orb_radius - 10) * math.sin(angle)
        draw.ellipse([x-1, y-1, x+1, y+1], fill=(230, 230, 250, 255))
    
    return img


def create_eyes_sprite(size=(200, 200), blink_state="open"):
    """Create the eyes layer"""
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Eye positions
    center_x, center_y = size[0] // 2, size[1] // 2
    left_eye_x, right_eye_x = center_x - 20, center_x + 20
    eye_y = center_y - 5
    eye_size = 10
    
    if blink_state == "open":
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
        pupil_size = 4
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
    
    elif blink_state == "closed":
        # Draw closed eyes (sleepy, gentle)
        # Left eye
        draw.arc([
            left_eye_x - eye_size, eye_y - 2,
            left_eye_x + eye_size, eye_y + 2
        ], start=0, end=180, fill=(47, 47, 47, 255), width=2)
        
        # Right eye
        draw.arc([
            right_eye_x - eye_size, eye_y - 2,
            right_eye_x + eye_size, eye_y + 2
        ], start=0, end=180, fill=(47, 47, 47, 255), width=2)
    
    return img


def create_mouth_sprite(size=(200, 200)):
    """Create the mouth layer"""
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Mouth position
    center_x, center_y = size[0] // 2, size[1] // 2
    mouth_y = center_y + 20
    mouth_width = 12
    mouth_height = 6
    
    # Draw minimal mouth (restrained expression)
    draw.arc([
        center_x - mouth_width//2, 
        mouth_y - mouth_height//4,
        center_x + mouth_width//2, 
        mouth_y + mouth_height//4
    ], start=10, end=170, fill=(250, 218, 221, 255), width=1)  # Light pink
    
    return img


def create_cheeks_sprite(size=(200, 200)):
    """Create the cheeks layer"""
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Cheek positions
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # Left cheek
    draw.ellipse([
        center_x - 35, center_y + 5,
        center_x - 25, center_y + 11
    ], fill=(255, 209, 220, 150))  # Light pink with transparency
    
    # Right cheek
    draw.ellipse([
        center_x + 25, center_y + 5,
        center_x + 35, center_y + 11
    ], fill=(255, 209, 220, 150))  # Light pink with transparency
    
    return img


def create_wings_sprite(size=(200, 200)):
    """Create the wings layer"""
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Wing positions
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # Left wing points
    left_wing_points = [
        (center_x - 60, center_y - 20),  # Wing tip
        (center_x - 75, center_y - 30),  # Upper attachment
        (center_x - 65, center_y),       # Lower attachment
        (center_x - 55, center_y - 5)    # Wing base
    ]
    draw.polygon(left_wing_points, fill=(230, 230, 250, 180))  # Light lavender with transparency
    
    # Right wing points
    right_wing_points = [
        (center_x + 60, center_y - 20),  # Wing tip
        (center_x + 75, center_y - 30),  # Upper attachment
        (center_x + 65, center_y),       # Lower attachment
        (center_x + 55, center_y - 5)    # Wing base
    ]
    draw.polygon(right_wing_points, fill=(230, 230, 250, 180))  # Light lavender with transparency
    
    return img


def create_soul_core_sprite(size=(200, 200), rotation=0, pulse=0):
    """Create the soul core layer"""
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Core position
    center_x, center_y = size[0] // 2, size[1] // 2
    core_size = 15
    
    # Draw core glow (soft, not flashy)
    glow_size = core_size + 5 + int(abs(math.sin(pulse)) * 3)
    draw.ellipse([
        center_x - glow_size, center_y - glow_size,
        center_x + glow_size, center_y + glow_size
    ], fill=(147, 112, 219, 100))  # Medium purple with transparency
    
    # Draw faceted soul shard
    core_points = []
    for i in range(8):
        angle = (i * 45 + rotation) * math.pi / 180
        radius = core_size * (0.8 + 0.2 * math.sin(i * 0.7))
        px = center_x + radius * math.cos(angle)
        py = center_y + radius * math.sin(angle)
        core_points.extend([px, py])
    
    draw.polygon(core_points, fill=(75, 0, 130, 255), outline=(122, 92, 148, 255), width=1)  # Indigo
    
    # Draw internal spiral of the soul shard
    spiral_points = []
    for i in range(20):
        angle = (i * 18 + rotation * 2) * math.pi / 180
        radius = core_size * 0.6 * (1 - i/20)
        px = center_x + radius * math.cos(angle)
        py = center_y + radius * math.sin(angle)
        spiral_points.extend([int(px), int(py)])
    
    if len(spiral_points) >= 4:
        draw.line(spiral_points, fill=(177, 156, 217, 200), width=1, joint="curve")
    
    return img


def create_party_hat_sprite(size=(200, 200)):
    """Create the party hat layer"""
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Hat position (slightly tilted)
    center_x, center_y = size[0] // 2, size[1] // 2
    hat_x, hat_y = center_x + 5, center_y - 25
    
    # Draw party hat (cone shape)
    hat_points = [
        (hat_x, hat_y - 15),      # Tip of hat
        (hat_x - 8, hat_y - 5),   # Left base
        (hat_x + 8, hat_y - 5)    # Right base
    ]
    draw.polygon(hat_points, fill=(255, 215, 0, 255), outline=(212, 175, 55, 255), width=1)  # Gold
    
    # Draw hat decoration (small circle)
    draw.ellipse([
        hat_x - 2, hat_y - 12, hat_x + 2, hat_y - 8
    ], fill=(255, 105, 180, 255))  # Pink
    
    return img


def composite_character_sprites(size=(200, 200), blink_state="open"):
    """Composite all sprites into a single character image"""
    # Create all layers
    orb = create_base_orb_sprite(size)
    eyes = create_eyes_sprite(size, blink_state)
    mouth = create_mouth_sprite(size)
    cheeks = create_cheeks_sprite(size)
    wings = create_wings_sprite(size)
    core = create_soul_core_sprite(size, rotation=0, pulse=0)
    hat = create_party_hat_sprite(size)
    
    # Composite layers in order
    result = Image.new('RGBA', size, (255, 255, 255, 0))
    result = Image.alpha_composite(result, orb)
    result = Image.alpha_composite(result, core)  # Core behind other elements
    result = Image.alpha_composite(result, cheeks)
    result = Image.alpha_composite(result, eyes)
    result = Image.alpha_composite(result, mouth)
    result = Image.alpha_composite(result, wings)
    result = Image.alpha_composite(result, hat)
    
    return result


def generate_animation_frames(num_frames=12):
    """Generate animation frames for the fairy orb"""
    frames = []
    
    for i in range(num_frames):
        # Calculate animation parameters
        float_x = math.sin(i * 2 * math.pi / num_frames) * 2.5
        float_y = math.sin(i * 2.5 * math.pi / num_frames) * 1.5
        core_rotation = (i * 30) % 360  # Rotate 30 degrees per frame
        core_pulse = i * 0.5
        wing_flap = math.sin(i * 2 * math.pi / num_frames) * 0.3
        
        # Create the base image
        img = Image.new('RGBA', (200, 200), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Apply floating offset to all elements
        center_x, center_y = 100 + float_x, 100 + float_y
        orb_radius = 60
        
        # Draw the orb body with offset
        draw.ellipse([
            center_x - orb_radius, 
            center_y - orb_radius, 
            center_x + orb_radius, 
            center_y + orb_radius
        ], fill=(240, 230, 255, 255), outline=(224, 208, 240, 255), width=1)
        
        # Add subtle texture
        for j in range(8):
            angle = (j * 45) * math.pi / 180
            x = center_x + (orb_radius - 10) * math.cos(angle)
            y = center_y + (orb_radius - 10) * math.sin(angle)
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(230, 230, 250, 255))
        
        # Draw eyes with offset
        left_eye_x, right_eye_x = center_x - 20, center_x + 20
        eye_y = center_y - 5
        eye_size = 10
        
        # Always open eyes in animation
        # Left eye
        draw.ellipse([
            left_eye_x - eye_size, eye_y - eye_size,
            left_eye_x + eye_size, eye_y + eye_size
        ], fill=(255, 255, 255, 255), outline=(208, 208, 208, 255), width=1)
        
        # Right eye
        draw.ellipse([
            right_eye_x - eye_size, eye_y - eye_size,
            right_eye_x + eye_size, eye_y + eye_y
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
        
        # Draw mouth with offset
        mouth_y = center_y + 20
        mouth_width = 12
        mouth_height = 6
        draw.arc([
            center_x - mouth_width//2, 
            mouth_y - mouth_height//4,
            center_x + mouth_width//2, 
            mouth_y + mouth_height//4
        ], start=10, end=170, fill=(250, 218, 221, 255), width=1)  # Light pink
        
        # Draw cheeks with offset
        # Left cheek
        draw.ellipse([
            center_x - 35, center_y + 5,
            center_x - 25, center_y + 11
        ], fill=(255, 209, 220, 150))  # Light pink with transparency
        
        # Right cheek
        draw.ellipse([
            center_x + 25, center_y + 5,
            center_x + 35, center_y + 11
        ], fill=(255, 209, 220, 150))  # Light pink with transparency
        
        # Draw soul core with rotation and pulse
        core_size = 15
        glow_size = core_size + 5 + int(abs(math.sin(core_pulse)) * 3)
        draw.ellipse([
            center_x - glow_size, center_y - glow_size,
            center_x + glow_size, center_y + glow_size
        ], fill=(147, 112, 219, 100))  # Medium purple with transparency
        
        # Draw faceted soul shard
        core_points = []
        for j in range(8):
            angle = (j * 45 + core_rotation) * math.pi / 180
            radius = core_size * (0.8 + 0.2 * math.sin(j * 0.7))
            px = center_x + radius * math.cos(angle)
            py = center_y + radius * math.sin(angle)
            core_points.extend([px, py])
        
        draw.polygon(core_points, fill=(75, 0, 130, 255), outline=(122, 92, 148, 255), width=1)  # Indigo
        
        # Draw internal spiral of the soul shard
        spiral_points = []
        for j in range(20):
            angle = (j * 18 + core_rotation * 2) * math.pi / 180
            radius = core_size * 0.6 * (1 - j/20)
            px = center_x + radius * math.cos(angle)
            py = center_y + radius * math.sin(angle)
            spiral_points.extend([int(px), int(py)])
        
        if len(spiral_points) >= 4:
            draw.line(spiral_points, fill=(177, 156, 217, 200), width=1, joint="curve")
        
        # Draw wings with flap offset
        # Left wing with offset and flap
        left_wing_points = [
            (center_x - 60, center_y - 20 + wing_flap),  # Wing tip with flap
            (center_x - 75, center_y - 30),             # Upper attachment
            (center_x - 65, center_y),                  # Lower attachment
            (center_x - 55, center_y - 5)               # Wing base
        ]
        draw.polygon(left_wing_points, fill=(230, 230, 250, 180))  # Light lavender with transparency
        
        # Right wing with offset and opposite flap
        right_wing_points = [
            (center_x + 60, center_y - 20 - wing_flap), # Wing tip with opposite flap
            (center_x + 75, center_y - 30),             # Upper attachment
            (center_x + 65, center_y),                  # Lower attachment
            (center_x + 55, center_y - 5)               # Wing base
        ]
        draw.polygon(right_wing_points, fill=(230, 230, 250, 180))  # Light lavender with transparency
        
        # Draw party hat with offset
        hat_x, hat_y = center_x + 5, center_y - 25
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
        
        frames.append(img)
    
    return frames


def save_sprites():
    """Save generated sprites to files"""
    # Create output directory
    os.makedirs("sprites", exist_ok=True)
    
    # Save individual sprites
    print("Creating individual sprites...")
    
    # Base orb
    orb_img = create_base_orb_sprite()
    orb_img.save("sprites/orb_base.png")
    
    # Eyes (open and closed)
    eyes_open = create_eyes_sprite(blink_state="open")
    eyes_closed = create_eyes_sprite(blink_state="closed")
    eyes_open.save("sprites/eyes_open.png")
    eyes_closed.save("sprites/eyes_closed.png")
    
    # Other individual sprites
    mouth_img = create_mouth_sprite()
    mouth_img.save("sprites/mouth.png")
    
    cheeks_img = create_cheeks_sprite()
    cheeks_img.save("sprites/cheeks.png")
    
    wings_img = create_wings_sprite()
    wings_img.save("sprites/wings.png")
    
    core_img = create_soul_core_sprite(rotation=0, pulse=0)
    core_img.save("sprites/soul_core.png")
    
    hat_img = create_party_hat_sprite()
    hat_img.save("sprites/party_hat.png")
    
    # Save composite image
    composite_img = composite_character_sprites(blink_state="open")
    composite_img.save("sprites/composite_character.png")
    
    # Generate and save animation frames
    print("Generating animation frames...")
    animation_frames = generate_animation_frames()
    
    for i, frame in enumerate(animation_frames):
        frame.save(f"sprites/animation_frame_{i:02d}.png")
    
    # Create a sample GIF animation
    animation_frames[0].save(
        "sprites/sample_animation.gif",
        save_all=True,
        append_images=animation_frames[1:],
        duration=100,  # 100ms per frame (10 FPS)
        loop=0  # Infinite loop
    )
    
    print("Sprite generation complete!")
    print("Files saved in 'sprites' directory:")
    print("- Individual sprite layers")
    print("- Composite character image")
    print("- Animation frames")
    print("- Sample animated GIF")


def main():
    print("Starting Sprite Generator for Aware Companion Fairy Orb...")
    print("Creating art sprites and animations based on the character description.")
    
    save_sprites()


if __name__ == "__main__":
    main()