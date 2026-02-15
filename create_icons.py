"""Create simple icons for PWA"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple medical icon"""
    # Create image with gradient background
    img = Image.new('RGB', (size, size), color='#667eea')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple medical cross
    cross_size = size // 2
    cross_thickness = size // 8
    center = size // 2
    
    # Vertical bar
    draw.rectangle([
        center - cross_thickness//2,
        center - cross_size//2,
        center + cross_thickness//2,
        center + cross_size//2
    ], fill='white')
    
    # Horizontal bar
    draw.rectangle([
        center - cross_size//2,
        center - cross_thickness//2,
        center + cross_size//2,
        center + cross_thickness//2
    ], fill='white')
    
    # Save
    img.save(filename, 'PNG')
    print(f'Created: {filename}')

# Create icons
static_dir = '/home/claude/medical_records_app/static'
create_icon(192, os.path.join(static_dir, 'icon-192.png'))
create_icon(512, os.path.join(static_dir, 'icon-512.png'))

print('Icons created successfully!')
