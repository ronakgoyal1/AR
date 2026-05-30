import os
from PIL import Image, ImageDraw, ImageFilter

def create_hoop(color, width, height, thickness):
    img = Image.new("RGBA", (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # Draw outer
    draw.ellipse((10, 10, width-10, height-10), outline=color, width=thickness)
    return img

def create_stud(color, size):
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((5, 5, size-5, size-5), fill=color)
    # highlight
    draw.ellipse((size*0.2, size*0.2, size*0.4, size*0.4), fill=(255,255,255,180))
    return img

def create_drop(top_color, bottom_color, w, h):
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((w//2-5, 5, w//2+5, 15), fill=top_color) # stud
    draw.line((w//2, 15, w//2, h-30), fill=(200,200,200,255), width=2) # chain
    draw.ellipse((10, h-40, w-10, h-10), fill=bottom_color) # drop
    draw.ellipse((w*0.3, h-35, w*0.5, h-25), fill=(255,255,255,150))
    return img

def create_jhumka(color, w, h):
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # top stud
    draw.ellipse((w//2-10, 5, w//2+10, 25), fill=color)
    draw.line((w//2, 25, w//2, 40), fill=color, width=2)
    # bell
    draw.chord((10, 20, w-10, h-20), start=180, end=360, fill=color)
    # danglers
    for i in range(15, w-15, 10):
        draw.ellipse((i-2, h-25, i+2, h-20), fill=color)
    return img

os.makedirs("backend/assets", exist_ok=True)

# 1. Minimal Gold Hoops
create_hoop((212, 175, 55, 255), 100, 100, 6).save("backend/assets/e1.png")
# 2. Minimal Silver Hoops
create_hoop((192, 192, 192, 255), 120, 120, 4).save("backend/assets/e2.png")
# 3. Premium Diamond Studs
create_stud((230, 240, 255, 255), 40).save("backend/assets/e3.png")
# 4. Pearl Drops
create_drop((212, 175, 55, 255), (240, 240, 230, 255), 80, 150).save("backend/assets/e4.png")
# 5. Elegant Danglers
create_drop((192, 192, 192, 255), (212, 175, 55, 255), 60, 180).save("backend/assets/e5.png")
# 6. Modern Jhumkas
create_jhumka((212, 175, 55, 255), 100, 120).save("backend/assets/e6.png")
# 7. Emerald Statement
create_drop((212, 175, 55, 255), (10, 120, 60, 255), 90, 140).save("backend/assets/e7.png")
# 8. Ruby Teardrop
create_drop((192, 192, 192, 255), (180, 20, 40, 255), 70, 130).save("backend/assets/e8.png")

print("Generated 8 sample assets.")
