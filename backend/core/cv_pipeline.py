import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageDraw
from .image_utils import apply_earring_overlay, color_adaptation
import os
import base64
import io
import logging

logger = logging.getLogger(__name__)

mp_face_mesh = mp.solutions.face_mesh
mp_face_detection = mp.solutions.face_detection

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)

face_detection = mp_face_detection.FaceDetection(
    model_selection=0, # 0 is best for close-range selfies
    min_detection_confidence=0.5
)

def create_hoop(color, width, height, thickness):
    img = Image.new("RGBA", (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((10, 10, width-10, height-10), outline=color, width=thickness)
    return img

def create_stud(color, size):
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((5, 5, size-5, size-5), fill=color)
    draw.ellipse((size*0.2, size*0.2, size*0.4, size*0.4), fill=(255,255,255,180))
    return img

def create_drop(top_color, bottom_color, w, h):
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((w//2-5, 5, w//2+5, 15), fill=top_color)
    draw.line((w//2, 15, w//2, h-30), fill=(200,200,200,255), width=2)
    draw.ellipse((10, h-40, w-10, h-10), fill=bottom_color)
    draw.ellipse((w*0.3, h-35, w*0.5, h-25), fill=(255,255,255,150))
    return img

def create_jhumka(color, w, h):
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((w//2-10, 5, w//2+10, 25), fill=color)
    draw.line((w//2, 25, w//2, 40), fill=color, width=2)
    draw.chord((10, 20, w-10, h-20), start=180, end=360, fill=color)
    for i in range(15, w-15, 10):
        draw.ellipse((i-2, h-25, i+2, h-20), fill=color)
    return img

def load_earring_asset(earring_id: str):
    path = f"assets/{earring_id}.png"
    if os.path.exists(path):
        return Image.open(path).convert("RGBA")
    
    # Fallbacks based on ID
    match earring_id:
        case "e1": return create_hoop((212, 175, 55, 255), 100, 100, 6) # Minimal Gold Hoops
        case "e2": return create_hoop((192, 192, 192, 255), 120, 120, 4) # Minimal Silver Hoops
        case "e3": return create_stud((230, 240, 255, 255), 40) # Premium Diamond Studs
        case "e4": return create_drop((212, 175, 55, 255), (240, 240, 230, 255), 80, 150) # Pearl Drops
        case "e5": return create_drop((192, 192, 192, 255), (212, 175, 55, 255), 60, 180) # Elegant Danglers
        case "e6": return create_jhumka((212, 175, 55, 255), 100, 120) # Modern Jhumkas
        case "e7": return create_drop((212, 175, 55, 255), (10, 120, 60, 255), 90, 140) # Emerald Statement
        case "e8": return create_drop((192, 192, 192, 255), (180, 20, 40, 255), 70, 130) # Ruby Teardrop
        case _: return create_drop((212, 175, 55, 255), (240, 240, 230, 255), 80, 150)

def get_landmarks(pil_image):
    # MediaPipe requires RGB images. Do NOT convert to BGR.
    img_rgb_arr = np.array(pil_image)
    
    logger.info("Running MediaPipe FaceMesh on RGB array...")
    results = face_mesh.process(img_rgb_arr)
    
    if not results.multi_face_landmarks:
        logger.warning("FaceMesh failed to detect landmarks. Trying fallback FaceDetection...")
        detection_results = face_detection.process(img_rgb_arr)
        if not detection_results.detections:
            logger.error("Fallback FaceDetection also failed.")
            return None, img_rgb_arr
        else:
            logger.error("Face detected via fallback, but no mesh landmarks available. Face might be occluded or blurry.")
            return None, img_rgb_arr

    logger.info("FaceMesh successfully detected landmarks.")
    return results.multi_face_landmarks[0], img_rgb_arr

def img_to_b64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=90)
    return "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode()

def classify_face_shape(landmarks, img_w, img_h):
    jaw_width = abs(landmarks.landmark[132].x - landmarks.landmark[361].x) * img_w
    cheek_width = abs(landmarks.landmark[234].x - landmarks.landmark[454].x) * img_w
    face_height = abs(landmarks.landmark[10].y - landmarks.landmark[152].y) * img_h
    
    ratio = face_height / cheek_width
    jaw_ratio = jaw_width / cheek_width
    
    if ratio > 1.4:
        return "Oval"
    elif jaw_ratio > 0.85:
        return "Square"
    elif jaw_ratio < 0.65:
        return "Heart"
    else:
        return "Round"

def calculate_head_pose(landmarks):
    left_z = landmarks.landmark[234].z
    right_z = landmarks.landmark[454].z
    yaw = (right_z - left_z) * 1.5 
    
    top_z = landmarks.landmark[10].z
    bottom_z = landmarks.landmark[152].z
    pitch = (bottom_z - top_z) * 1.5
    
    return yaw, pitch

def process_tryon(pil_image: Image.Image, earring_id: str):
    landmarks, cv_rgb_image = get_landmarks(pil_image)
    if not landmarks:
        raise ValueError("No face detected in the image. Please ensure your face is clearly visible, well-lit, and not obstructed.")
        
    img_h, img_w, _ = cv_rgb_image.shape
    
    lx = (landmarks.landmark[132].x + landmarks.landmark[177].x) / 2
    ly = (landmarks.landmark[132].y + landmarks.landmark[177].y) / 2
    left_ear = (lx * img_w, ly * img_h)
    
    rx = (landmarks.landmark[361].x + landmarks.landmark[401].x) / 2
    ry = (landmarks.landmark[361].y + landmarks.landmark[401].y) / 2
    right_ear = (rx * img_w, ry * img_h)
    
    face_left = landmarks.landmark[234]
    face_right = landmarks.landmark[454]
    face_width = np.sqrt(
        (face_right.x * img_w - face_left.x * img_w)**2 + 
        (face_right.y * img_h - face_left.y * img_h)**2
    )
    
    dy = face_right.y * img_h - face_left.y * img_h
    dx = face_right.x * img_w - face_left.x * img_w
    angle = np.degrees(np.arctan2(dy, dx))
    
    yaw, pitch = calculate_head_pose(landmarks)
    face_shape = classify_face_shape(landmarks, img_w, img_h)
    
    logger.info("Loading earring asset...")
    earring_img = load_earring_asset(earring_id)
    
    logger.info("Applying color adaptation...")
    earring_img = color_adaptation(cv_rgb_image, earring_img)
    
    variations = []
    scales = [1.0, 0.9, 1.1]
    scores = [0.95, 0.88, 0.85]
    
    for scale, score in zip(scales, scores):
        img_v = pil_image.copy()
        tryon_result = apply_earring_overlay(
            img_v, earring_img, 
            left_ear=left_ear,
            right_ear=right_ear,
            face_width=face_width,
            angle=angle,
            yaw=yaw,
            pitch=pitch,
            variation_scale=scale
        )
        
        variations.append({
            "image": img_to_b64(tryon_result), 
            "score": score,
            "scale": scale
        })
    
    variations.sort(key=lambda x: x["score"], reverse=True)
    return {
        "variations": variations,
        "face_shape": face_shape
    }
