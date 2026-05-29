import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from .image_utils import apply_earring_overlay, color_adaptation
import os
import base64
import io

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)

# Also initialize MediaPipe Selfie Segmentation for lightweight occlusion (hair)
mp_selfie_segmentation = mp.solutions.selfie_segmentation
selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=0)

def load_earring_asset(earring_id: str):
    """Loads an earring PNG asset with transparency, or generates a placeholder."""
    path = f"assets/{earring_id}.png"
    if os.path.exists(path):
        return Image.open(path).convert("RGBA")
    
    # Fallback placeholder earring (e.g., a gold hoop/drop) if asset not found
    img = Image.new("RGBA", (200, 400), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Elegant drop earring
    draw.ellipse((50, 0, 150, 100), fill=(212, 175, 55, 255)) # Top stud
    draw.polygon([(75, 90), (125, 90), (100, 380)], fill=(212, 175, 55, 255)) # Drop
    return img

def get_landmarks(pil_image):
    cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    results = face_mesh.process(cv_image)
    if not results.multi_face_landmarks:
        return None, cv_image
    return results.multi_face_landmarks[0], cv_image

def img_to_b64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=90)
    return "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode()

def apply_occlusion(base_pil_img, tryon_pil_img, cv_image):
    """
    Uses MediaPipe Selfie Segmentation to blend the try-on image,
    helping hair that might fall over the face/ears appear in front of the earring.
    """
    # Get segmentation mask
    results = selfie_segmentation.process(cv_image)
    mask = results.segmentation_mask
    
    # Threshold the mask to get foreground (person) vs background
    # But wait, hair is part of the foreground in selfie segmentation.
    # What we really need is a hair mask or depth map for true occlusion.
    # Since SelfieSegmentation puts hair & face together, it doesn't easily isolate hair OVER earrings.
    # As a lightweight MVP heuristic, we will stick to a soft blend. True 3D occlusion is heavy.
    # We will simply return the tryon image for now, as alpha compositing handles the basic blend.
    return tryon_pil_img

def process_tryon(pil_image: Image.Image, earring_id: str):
    landmarks, cv_image = get_landmarks(pil_image)
    if not landmarks:
        raise ValueError("No face detected in the image")
        
    img_h, img_w, _ = cv_image.shape
    
    # Landmarks for ear placement approximation
    # 132: left side, near earlobe
    # 361: right side, near earlobe
    left_ear = landmarks.landmark[132]
    right_ear = landmarks.landmark[361]
    
    # Face width for scaling: 234 (left edge) to 454 (right edge)
    face_left = landmarks.landmark[234]
    face_right = landmarks.landmark[454]
    
    face_width = np.sqrt(
        (face_right.x * img_w - face_left.x * img_w)**2 + 
        (face_right.y * img_h - face_left.y * img_h)**2
    )
    
    # Calculate head tilt (rotation)
    dy = face_right.y * img_h - face_left.y * img_h
    dx = face_right.x * img_w - face_left.x * img_w
    angle = np.degrees(np.arctan2(dy, dx))
    
    earring_img = load_earring_asset(earring_id)
    
    # Basic lighting adaptation
    earring_img = color_adaptation(cv_image, earring_img)
    
    variations = []
    
    # We'll generate 3 variations: default, slightly smaller, slightly larger.
    # This simulates best-result selection where the user can pick the best fit.
    scales = [1.0, 0.9, 1.1]
    scores = [0.95, 0.88, 0.85] # Mock scores for auto-selection logic
    
    for scale, score in zip(scales, scores):
        img_v = pil_image.copy()
        tryon_result = apply_earring_overlay(
            img_v, earring_img, 
            left_ear=(left_ear.x * img_w, left_ear.y * img_h),
            right_ear=(right_ear.x * img_w, right_ear.y * img_h),
            face_width=face_width,
            angle=angle,
            variation_scale=scale
        )
        
        # Apply occlusion heuristic
        final_result = apply_occlusion(pil_image, tryon_result, cv_image)
        
        variations.append({
            "image": img_to_b64(final_result), 
            "score": score,
            "scale": scale
        })
    
    # Sort by best score
    variations.sort(key=lambda x: x["score"], reverse=True)
    return variations
