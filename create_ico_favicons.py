from PIL import Image, ImageDraw

def create_padlock_ico():
    """Create a padlock favicon in ICO format"""
    # Create multiple sizes for ICO file
    sizes = [(16, 16), (32, 32), (48, 48)]
    images = []
    
    for size in sizes:
        # Create a new image with transparent background
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Scale factors
        scale_x = size[0] / 32
        scale_y = size[1] / 32
        
        # Draw shackle (top part) - silver/gray
        shackle_color = (192, 192, 192, 255)  # Silver
        # Simplified shackle arc
        draw.arc(
            [int(10*scale_x), int(4*scale_y), int(22*scale_x), int(16*scale_y)],
            start=180, end=0,
            fill=shackle_color, width=int(2*min(scale_x, scale_y))
        )
        
        # Draw lock body - gold gradient effect
        body_color = (255, 215, 0, 255)  # Gold
        draw.rounded_rectangle(
            [int(6*scale_x), int(14*scale_y), int(26*scale_x), int(28*scale_y)],
            radius=int(2*min(scale_x, scale_y)),
            fill=body_color,
            outline=(204, 172, 0, 255),
            width=1
        )
        
        # Draw keyhole
        keyhole_color = (26, 26, 26, 255)  # Dark gray
        # Keyhole circle
        draw.ellipse(
            [int(14*scale_x), int(18*scale_y), int(18*scale_x), int(22*scale_y)],
            fill=keyhole_color
        )
        # Keyhole slot
        draw.rectangle(
            [int(15*scale_x), int(20*scale_y), int(17*scale_x), int(25*scale_y)],
            fill=keyhole_color
        )
        
        images.append(img)
    
    # Save as ICO with multiple sizes
    images[0].save(
        'static/favicon-padlock.ico',
        format='ICO',
        sizes=[(16, 16), (32, 32), (48, 48)],
        append_images=images[1:]
    )
    print("Created favicon-padlock.ico")

def create_hexagon_ico():
    """Create a hexagon favicon in ICO format"""
    sizes = [(16, 16), (32, 32), (48, 48)]
    images = []
    
    for size in sizes:
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Scale factors
        scale_x = size[0] / 32
        scale_y = size[1] / 32
        
        # Calculate hexagon points
        cx, cy = size[0] // 2, size[1] // 2
        radius = min(size[0], size[1]) * 0.4
        
        # Hexagon vertices
        points = []
        for i in range(6):
            angle = i * 60 - 30  # Start at top
            x = cx + radius * __import__('math').cos(__import__('math').radians(angle))
            y = cy + radius * __import__('math').sin(__import__('math').radians(angle))
            points.append((x, y))
        
        # Draw filled hexagon with gold gradient
        draw.polygon(points, fill=(255, 215, 0, 255), outline=(255, 255, 255, 200), width=1)
        
        # Add inner highlight for depth
        inner_radius = radius * 0.6
        inner_points = []
        for i in range(6):
            angle = i * 60 - 30
            x = cx + inner_radius * __import__('math').cos(__import__('math').radians(angle))
            y = cy + inner_radius * __import__('math').sin(__import__('math').radians(angle))
            inner_points.append((x, y))
        
        # Draw inner hexagon outline for depth
        draw.polygon(inner_points, fill=None, outline=(255, 255, 255, 100), width=1)
        
        # Add "AN" text if size is large enough
        if size[0] >= 32:
            try:
                from PIL import ImageFont
                # Try to use a basic font
                font = ImageFont.load_default()
                text = "AN"
                # Get text bounding box
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = cx - text_width // 2
                text_y = cy - text_height // 2
                draw.text((text_x, text_y), text, fill=(26, 26, 26, 255), font=font)
            except:
                pass  # Skip text if font issues
        
        images.append(img)
    
    # Save as ICO
    images[0].save(
        'static/favicon-hexagon.ico',
        format='ICO',
        sizes=[(16, 16), (32, 32), (48, 48)],
        append_images=images[1:]
    )
    print("Created favicon-hexagon.ico")

if __name__ == "__main__":
    create_padlock_ico()
    create_hexagon_ico()
    print("✓ Both ICO favicons created successfully!")