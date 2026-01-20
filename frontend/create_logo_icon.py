#!/usr/bin/env python3
"""
Create app icon with ARCUS gothic logo
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import sys

try:
    # Create icons directory
    frontend_dir = Path(__file__).parent
    frontend_dir.mkdir(exist_ok=True)
    
    # Function to create icon with ARCUS text
    def create_arcus_icon(size, output_path):
        # Create black background
        img = Image.new('RGB', (size, size), color='#000000')
        draw = ImageDraw.Draw(img)
        
        # Try different fonts (system fonts that might have gothic/blackletter style)
        fonts_to_try = [
            ('Times New Roman', size // 2),
            ('Georgia', size // 2),
            ('serif', size // 2),
        ]
        
        font = None
        font_size = size // 2
        
        for font_name, fs in fonts_to_try:
            try:
                font = ImageFont.truetype(font_name, fs)
                break
            except:
                try:
                    font = ImageFont.truetype(font_name, fs - 10)
                    break
                except:
                    continue
        
        if font is None:
            # Fallback to default font
            font = ImageFont.load_default()
            font_size = size // 3
        
        # Get text size and center it
        text = "ARCUS"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size - text_width) // 2, (size - text_height) // 2 - 5)
        
        # Draw white "ARCUS" with glow effect (multiple layers for glow)
        # Outer glow layers
        for offset_x in range(-2, 3):
            for offset_y in range(-2, 3):
                if offset_x != 0 or offset_y != 0:
                    draw.text(
                        (position[0] + offset_x, position[1] + offset_y),
                        text,
                        fill=(255, 255, 255, 30),
                        font=font
                    )
        
        # Main white text
        draw.text(position, text, fill='white', font=font)
        
        img.save(output_path)
        print(f"Created {output_path} ({size}x{size})")
    
    # Create icons
    create_arcus_icon(192, frontend_dir / "icon-192.png")
    create_arcus_icon(512, frontend_dir / "icon-512.png")
    
    print("\nIcons created with ARCUS logo!")
    print("These will be used as app icons on iPhone when you add to home screen.")
    
except ImportError:
    print("Pillow library not found.")
    print("Run: pip install Pillow")
    print("Then run: python create_logo_icon.py")
except Exception as e:
    print(f"Error creating icons: {e}")
    print("\nYou can manually create icons:")
    print("1. Create 192x192 and 512x512 pixel images")
    print("2. Black background")
    print("3. White 'ARCUS' text in gothic/blackletter font")
    print("4. Save as icon-192.png and icon-512.png in frontend folder")
