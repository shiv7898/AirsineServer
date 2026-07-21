import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from PIL import Image, ImageDraw, ImageOps
except ImportError:
    print("PIL (Pillow) is not installed. Installing Pillow...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageDraw, ImageOps

def make_circular(img_path, output_path):
    img = Image.open(img_path).convert("RGBA")
    
    # Create mask
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    
    # Draw a circle on the mask
    draw.ellipse((0, 0) + img.size, fill=255)
    
    # Apply mask
    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    
    output.save(output_path, "PNG")
    print(f"Circular image saved successfully to {output_path}")

if __name__ == "__main__":
    src = "web/statics/admin/assets/images/logo1.png"
    dest = "web/statics/admin/assets/images/favicon.png"
    make_circular(src, dest)
