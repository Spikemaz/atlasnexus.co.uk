from PIL import Image, ImageDraw

def create_padlock_ico():
    """Create a padlock favicon in ICO format with black outline"""
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
        
        # Draw shackle (top part) - silver/gray with BLACK outline
        shackle_color = (192, 192, 192, 255)  # Silver
        outline_color = (0, 0, 0, 255)  # Black outline
        
        # Draw shackle with outline
        draw.arc(
            [int(10*scale_x), int(4*scale_y), int(22*scale_x), int(16*scale_y)],
            start=180, end=0,
            fill=outline_color, width=int(3*min(scale_x, scale_y))
        )
        draw.arc(
            [int(11*scale_x), int(5*scale_y), int(21*scale_x), int(15*scale_y)],
            start=180, end=0,
            fill=shackle_color, width=int(2*min(scale_x, scale_y))
        )
        
        # Draw lock body - gold with BLACK outline
        body_color = (255, 215, 0, 255)  # Gold
        draw.rounded_rectangle(
            [int(6*scale_x), int(14*scale_y), int(26*scale_x), int(28*scale_y)],
            radius=int(2*min(scale_x, scale_y)),
            fill=body_color,
            outline=outline_color,
            width=2
        )
        
        # Draw keyhole with black outline
        keyhole_color = (26, 26, 26, 255)  # Dark gray
        # Keyhole circle
        draw.ellipse(
            [int(14*scale_x), int(18*scale_y), int(18*scale_x), int(22*scale_y)],
            fill=keyhole_color,
            outline=outline_color,
            width=1
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
    """Create a hexagon favicon in ICO format with website blue colors"""
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
        
        # Website blue colors
        blue_primary = (96, 165, 250, 255)  # #60a5fa
        blue_light = (147, 197, 253, 255)   # #93c5fd
        blue_dark = (59, 130, 246, 255)     # #3b82f6
        
        # Draw filled hexagon with light fill and thick blue outline
        draw.polygon(points, fill=(147, 197, 253, 40), outline=blue_primary, width=3)
        
        # Add inner hexagon for depth
        inner_radius = radius * 0.65
        inner_points = []
        for i in range(6):
            angle = i * 60 - 30
            x = cx + inner_radius * __import__('math').cos(__import__('math').radians(angle))
            y = cy + inner_radius * __import__('math').sin(__import__('math').radians(angle))
            inner_points.append((x, y))
        
        # Draw inner hexagon outline for depth
        draw.polygon(inner_points, fill=None, outline=blue_light, width=1)
        
        # Add center dot for visual anchor
        if size[0] >= 16:
            dot_radius = max(1, int(2 * min(scale_x, scale_y)))
            draw.ellipse(
                [cx - dot_radius, cy - dot_radius, cx + dot_radius, cy + dot_radius],
                fill=blue_primary
            )
        
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