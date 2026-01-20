#!/usr/bin/env python3
"""
Create app icons for PWA
This will generate simple colored icons if PIL is available, 
otherwise provides instructions for creating them manually.
"""
from pathlib import Path
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
    
    def create_icon(size, output_path):
        # Create a simple icon with Arcus branding
        img = Image.new('RGB', (size, size), color='#2563eb')
        draw = ImageDraw.Draw(img)
        
        # Draw a simple "A" letter in the center
        try:
            # Try to use a larger font
            font_size = size // 2
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", size // 3)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
        
        # Get text size and center it
        text = "A"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size - text_width) // 2, (size - text_height) // 2)
        
        # Draw white "A"
        draw.text(position, text, fill='white', font=font)
        
        img.save(output_path)
        print(f"Created {output_path} ({size}x{size})")
    
    # Create icons directory
    frontend_dir = Path(__file__).parent / "frontend"
    frontend_dir.mkdir(exist_ok=True)
    
    # Create icons
    create_icon(192, frontend_dir / "icon-192.png")
    create_icon(512, frontend_dir / "icon-512.png")
    
    print("\nIcons created successfully!")
    print("You can now use the app and add it to your home screen.")
    
except ImportError:
    print("Pillow library not found. Creating simple placeholder instructions...")
    print("\nTo create icons manually:")
    print("1. Create two square images (192x192 and 512x512 pixels)")
    print("2. Use a blue background (#2563eb) with white 'A' letter")
    print("3. Save them as:")
    print("   - frontend/icon-192.png")
    print("   - frontend/icon-512.png")
    print("\nOr install Pillow and run this script again:")
    print("   pip install Pillow")
    print("   python create_icons.py")

