import os
from PIL import Image, ImageDraw, ImageFont

icons_dir = "/home/grogulover5/Desktop/GalacticDefenders/icons"
if not os.path.exists(icons_dir):
    os.makedirs(icons_dir)

# Create a 1024x1024 base image
size = 1024
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw a dark blue circular background
draw.ellipse((64, 64, size-64, size-64), fill=(20, 30, 60))

# Draw a glowing cyan border
draw.ellipse((64, 64, size-64, size-64), outline=(0, 255, 255), width=20)

# Draw a stylized spaceship (triangle)
center_x = size // 2
center_y = size // 2
draw.polygon([
    (center_x, center_y - 250),       # Top
    (center_x - 200, center_y + 200), # Bottom Left
    (center_x, center_y + 100),       # Bottom Center
    (center_x + 200, center_y + 200)  # Bottom Right
], fill=(0, 150, 255))

# Draw engine thrust
draw.polygon([
    (center_x - 50, center_y + 120),
    (center_x + 50, center_y + 120),
    (center_x, center_y + 300)
], fill=(255, 100, 0))

# Save sizes
sizes_ico = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
img.save(os.path.join(icons_dir, "icon.ico"), format="ICO", sizes=sizes_ico)

img.save(os.path.join(icons_dir, "icon.png"), format="PNG")

try:
    img.save(os.path.join(icons_dir, "icon.icns"), format="ICNS")
except Exception as e:
    print(f"Error saving icns: {e}")

print("Icons generated successfully!")
