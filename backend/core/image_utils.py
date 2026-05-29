from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import numpy as np
import cv2

def apply_noise(pil_image: Image.Image, amount: float = 0.02) -> Image.Image:
    """Adds subtle gaussian noise to harmonize the CGI overlay with real photos."""
    img_array = np.array(pil_image, dtype=np.float32)
    noise = np.random.normal(0, amount * 255, img_array.shape)
    
    # Only apply noise to non-transparent areas (where alpha > 0)
    if img_array.shape[2] == 4:
        mask = img_array[:, :, 3] > 0
        img_array[mask, :3] = img_array[mask, :3] + noise[mask, :3]
    else:
        img_array[:, :, :3] = img_array[:, :, :3] + noise[:, :, :3]
        
    img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    return Image.fromarray(img_array)

def adaptive_metallic_reflection(fg_pil_img: Image.Image, mean_brightness: float) -> Image.Image:
    """
    Adjusts the intensity of the 'metallic' shine/contrast based on the overall 
    brightness of the selfie. Bright environments get sharper highlights.
    """
    # Base normalization (128 is mid-tone)
    brightness_factor = max(0.6, min(1.4, mean_brightness / 128.0))
    contrast_factor = 1.0 + ((mean_brightness - 128.0) / 255.0) * 0.5
    
    enhancer_b = ImageEnhance.Brightness(fg_pil_img)
    fg_pil_img = enhancer_b.enhance(brightness_factor)
    
    enhancer_c = ImageEnhance.Contrast(fg_pil_img)
    fg_pil_img = enhancer_c.enhance(contrast_factor)
    
    return fg_pil_img

def color_adaptation(bg_cv_img, fg_pil_img):
    """
    Matches the overall brightness and adds metallic reflection tuning.
    """
    gray = cv2.cvtColor(bg_cv_img, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)
    
    fg_pil_img = adaptive_metallic_reflection(fg_pil_img, mean_brightness)
    fg_pil_img = apply_noise(fg_pil_img, amount=0.015) # Very subtle grain
    
    return fg_pil_img

def apply_feathering(pil_img: Image.Image, radius: int = 1) -> Image.Image:
    """Feathers the edges to remove harsh cut-out artifacts."""
    if pil_img.mode != 'RGBA':
        return pil_img
        
    alpha = pil_img.split()[3]
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius))
    
    result = pil_img.copy()
    result.putalpha(alpha)
    return result

def create_multi_layer_shadow(earring_img: Image.Image) -> Image.Image:
    """Creates a realistic two-tier shadow (contact shadow + soft ambient shadow)."""
    shadow_base = earring_img.copy().convert("RGBA")
    shadow_data = np.array(shadow_base)
    
    # Make all pixels black, keeping alpha
    shadow_data[:, :, 0:3] = 0
    shadow_base = Image.fromarray(shadow_data)
    
    # 1. Contact shadow (tight, dark)
    contact_shadow = shadow_base.copy()
    contact_data = np.array(contact_shadow)
    contact_data[:, :, 3] = (contact_data[:, :, 3] * 0.6).astype(np.uint8)
    contact_shadow = Image.fromarray(contact_data).filter(ImageFilter.GaussianBlur(2))
    
    # 2. Ambient shadow (wide, soft)
    ambient_shadow = shadow_base.copy()
    ambient_data = np.array(ambient_shadow)
    ambient_data[:, :, 3] = (ambient_data[:, :, 3] * 0.3).astype(np.uint8)
    ambient_shadow = Image.fromarray(ambient_data).filter(ImageFilter.GaussianBlur(8))
    
    # Combine shadows
    combined = Image.new("RGBA", shadow_base.size, (0,0,0,0))
    combined.alpha_composite(ambient_shadow, (0, 0))
    combined.alpha_composite(contact_shadow, (0, 0))
    
    return combined

def apply_earring_overlay(base_img: Image.Image, earring_img: Image.Image, 
                          left_ear: tuple, right_ear: tuple, 
                          face_width: float, angle: float, variation_scale: float = 1.0):
    """
    Overlays the earring with advanced compositing.
    """
    result_img = base_img.convert("RGBA")
    
    target_w = int(face_width * 0.15 * variation_scale)
    aspect_ratio = earring_img.height / earring_img.width
    target_h = int(target_w * aspect_ratio)
    
    if target_w <= 0 or target_h <= 0:
        return base_img.convert("RGB")
        
    resized_earring = earring_img.resize((target_w, target_h), Image.LANCZOS)
    
    # Feather edges
    resized_earring = apply_feathering(resized_earring, radius=1)
    
    # Left Ear Processing
    left_earring = resized_earring.copy().rotate(-angle, expand=True, resample=Image.BICUBIC)
    left_shadow = create_multi_layer_shadow(left_earring)
    
    lw, lh = left_earring.size
    lx = int(left_ear[0] - lw / 2)
    ly = int(left_ear[1])
    
    # Apply slightly offset shadows
    result_img.alpha_composite(left_shadow, (lx + 2, ly + 4))
    result_img.alpha_composite(left_earring, (lx, ly))
    
    # Right Ear Processing
    right_earring = resized_earring.transpose(Image.FLIP_LEFT_RIGHT).rotate(-angle, expand=True, resample=Image.BICUBIC)
    right_shadow = create_multi_layer_shadow(right_earring)
    
    rw, rh = right_earring.size
    rx = int(right_ear[0] - rw / 2)
    ry = int(right_ear[1])
    
    result_img.alpha_composite(right_shadow, (rx - 2, ry + 4))
    result_img.alpha_composite(right_earring, (rx, ry))
    
    return result_img.convert("RGB")
