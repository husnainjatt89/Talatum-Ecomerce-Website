"""
Create placeholder images for Talatum.
Run: python talatum/create_placeholder.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

# Ensure output directory exists
out_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')
os.makedirs(out_dir, exist_ok=True)


def make_placeholder(path, width=400, height=400, bg=(220, 220, 220),
                     fg=(150, 150, 150), text='No Image'):
    img = Image.new('RGB', (width, height), color=bg)
    draw = ImageDraw.Draw(img)

    # Draw a simple camera / image icon using rectangles
    cx, cy = width // 2, height // 2
    # Outer frame
    draw.rectangle([cx - 60, cy - 45, cx + 60, cy + 45],
                   outline=fg, width=3)
    # Lens circle
    draw.ellipse([cx - 25, cy - 25, cx + 25, cy + 25],
                 outline=fg, width=3)
    # Small circle (lens highlight)
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8],
                 fill=fg)

    # Text label
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy + 60), text, fill=fg, font=font)

    img.save(path)
    print(f'  Created: {path}')


def make_avatar(path, size=200, bg=(180, 180, 180), fg=(120, 120, 120)):
    img = Image.new('RGB', (size, size), color=bg)
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    # Head circle
    r_head = size // 5
    draw.ellipse([cx - r_head, cy - r_head - 10,
                  cx + r_head, cy + r_head - 10], fill=fg)

    # Body arc
    draw.arc([cx - size // 3, cy + 10,
              cx + size // 3, cy + size // 2 + 20],
             start=0, end=180, fill=fg, width=4)

    img.save(path)
    print(f'  Created: {path}')


if __name__ == '__main__':
    print('Creating placeholder images...')
    make_placeholder(os.path.join(out_dir, 'placeholder.jpg'))
    make_avatar(os.path.join(out_dir, 'default-avatar.png'))
    print('Done.')
