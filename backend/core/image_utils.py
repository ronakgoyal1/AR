from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2

def apply_noise(pil_image: Image.Image, amount: float = 0.02) -> Image.Image:
    img_array = np.array(pil_image, dtype=np.float32)
    noise = np.random.normal(0, amount * 255, img_array.shape)
    
    if img_array.shape[2] == 4:
        mask = img_array[:, :, 3] > 0
        img_array[mask, :3] = img_array[mask, :3] + noise[mask, :3]
    else:
        img_array[:, :, :3] = img_array[:, :, :3] + noise[:, :, :3]
        
    img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    return Image.fromarray(img_array)

def adaptive_metallic_reflection(fg_pil_img: Image.Image, mean_brightness: float) -> Image.Image:
    brightness_factor = max(0.6, min(1.4, mean_brightness / 128.0))
    contrast_factor = 1.0 + ((mean_brightness - 128.0) / 255.0) * 0.5
    
    enhancer_b = ImageEnhance.Brightness(fg_pil_img)
    fg_pil_img = enhancer_b.enhance(brightness_factor)
    
    enhancer_c = ImageEnhance.Contrast(fg_pil_img)
    fg_pil_img = enhancer_c.enhance(contrast_factor)
    return fg_pil_img

def color_adaptation(bg_cv_img, fg_pil_img):
    gray = cv2.cvtColor(bg_cv_img, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)
    fg_pil_img = adaptive_metallic_reflection(fg_pil_img, mean_brightness)
    fg_pil_img = apply_noise(fg_pil_img, amount=0.015)
    return fg_pil_img

def apply_feathering(pil_img: Image.Image, radius: int = 1) -> Image.Image:
    if pil_img.mode != 'RGBA': return pil_img
    alpha = pil_img.split()[3].filter(ImageFilter.GaussianBlur(radius))
    result = pil_img.copy()
    result.putalpha(alpha)
    return result

def create_multi_layer_shadow(earring_img: Image.Image) -> Image.Image:
    shadow_base = earring_img.copy().convert("RGBA")
    shadow_data = np.array(shadow_base)
    shadow_data[:, :, 0:3] = 0
    shadow_base = Image.fromarray(shadow_data)
    
    contact_shadow = shadow_base.copy()
    contact_data = np.array(contact_shadow)
    contact_data[:, :, 3] = (contact_data[:, :, 3] * 0.6).astype(np.uint8)
    contact_shadow = Image.fromarray(contact_data).filter(ImageFilter.GaussianBlur(2))
    
    ambient_shadow = shadow_base.copy()
    ambient_data = np.array(ambient_shadow)
    ambient_data[:, :, 3] = (ambient_data[:, :, 3] * 0.3).astype(np.uint8)
    ambient_shadow = Image.fromarray(ambient_data).filter(ImageFilter.GaussianBlur(8))
    
    combined = Image.new("RGBA", shadow_base.size, (0,0,0,0))
    combined.alpha_composite(ambient_shadow, (0, 0))
    combined.alpha_composite(contact_shadow, (0, 0))
    return combined

def apply_perspective_warp(earring_img: Image.Image, yaw: float, pitch: float, is_left_ear: bool) -> Image.Image:
    """
    Applies a simple affine transformation based on head yaw and pitch to create a 3D effect.
    """
    w, h = earring_img.size
    
    # Simple foreshortening based on yaw
    # If looking left (yaw > 0), left ear is foreshortened, right ear is flatter
    yaw_factor = max(0.3, 1.0 - abs(yaw * 0.5)) if (yaw > 0 and is_left_ear) or (yaw < 0 and not is_left_ear) else 1.0
    
    new_w = int(w * yaw_factor)
    new_w = max(10, new_w) # prevent scaling to 0
    
    # We can also shear vertically for pitch
    pitch_factor = pitch * 0.2
    
    resized = earring_img.resize((new_w, h), Image.LANCZOS)
    
    # Apply shear via Affine transform in PIL (1, shear_x, 0, shear_y, 1, 0)
    # We use shear_y based on pitch
    shear_y = pitch_factor if is_left_ear else -pitch_factor
    
    # Prevent extreme uncanniness
    shear_y = max(-0.3, min(0.3, shear_y))
    
    # Data is (a, b, c, d, e, f):
    # x' = ax + by + c
    # y' = dx + ey + f
    transformed = resized.transform(
        (new_w, int(h * 1.2)), # expanded canvas for shear
        Image.AFFINE,
        (1, 0, 0, shear_y, 1, 0),
        resample=Image.BICUBIC
    )
    return transformed

def apply_earring_overlay(base_img: Image.Image, earring_img: Image.Image, 
                          left_ear: tuple, right_ear: tuple, 
                          face_width: float, angle: float, 
                          yaw: float, pitch: float, variation_scale: float = 1.0):
    
    result_img = base_img.convert("RGBA")
    
    target_w = int(face_width * 0.15 * variation_scale)
    aspect_ratio = earring_img.height / earring_img.width
    target_h = int(target_w * aspect_ratio)
    
    if target_w <= 0 or target_h <= 0: return base_img.convert("RGB")
    
    resized_earring = earring_img.resize((target_w, target_h), Image.LANCZOS)
    resized_earring = apply_feathering(resized_earring, radius=1)
    
    # Left Ear
    left_earring = apply_perspective_warp(resized_earring, yaw, pitch, is_left_ear=True)
    left_earring = left_earring.rotate(-angle, expand=True, resample=Image.BICUBIC)
    
    left_shadow = create_multi_layer_shadow(left_earring)
    lw, lh = left_earring.size
    lx, ly = int(left_ear[0] - lw / 2), int(left_ear[1])
    
    # Basic occlusion masking: fade the top 10% of the earring so hair/lobe looks like it's in front
    occlusion_mask = Image.new("L", left_earring.size, 255)
    for y in range(int(lh * 0.1)):
        alpha = int((y / (lh * 0.1)) * 255)
        for x in range(lw):
            occlusion_mask.putpixel((x, y), alpha)
    left_earring.putalpha(Image.composite(left_earring.split()[3], Image.new("L", left_earring.size, 0), occlusion_mask))
    
    result_img.alpha_composite(left_shadow, (lx + 2, ly + 4))
    result_img.alpha_composite(left_earring, (lx, ly))
    
    # Right Ear
    right_earring = resized_earring.transpose(Image.FLIP_LEFT_RIGHT)
    right_earring = apply_perspective_warp(right_earring, yaw, pitch, is_left_ear=False)
    right_earring = right_earring.rotate(-angle, expand=True, resample=Image.BICUBIC)
    
    right_shadow = create_multi_layer_shadow(right_earring)
    rw, rh = right_earring.size
    rx, ry = int(right_ear[0] - rw / 2), int(right_ear[1])
    
    occlusion_mask_r = Image.new("L", right_earring.size, 255)
    for y in range(int(rh * 0.1)):
        alpha = int((y / (rh * 0.1)) * 255)
        for x in range(rw):
            occlusion_mask_r.putpixel((x, y), alpha)
    right_earring.putalpha(Image.composite(right_earring.split()[3], Image.new("L", right_earring.size, 0), occlusion_mask_r))
    
    result_img.alpha_composite(right_shadow, (rx - 2, ry + 4))
    result_img.alpha_composite(right_earring, (rx, ry))
    
    return result_img.convert("RGB")
