import cv2
import numpy as np
import hashlib
import random
import os

def generate_color_shares(image_path):
    img = cv2.imread(image_path)
    if img is None: return None, None, None, None
    h, w, c = img.shape

    # Innovation: Integrity Hash (Fragile Watermark)
    integrity_seal = hashlib.sha256(img.tobytes()).hexdigest()

    # XOR Splitting
    share1 = np.random.randint(0, 256, (h, w, c), dtype=np.uint8)
    share2 = cv2.bitwise_xor(img, share1)
    
    otp = str(random.randint(100000, 999999))
    return share1, share2, integrity_seal, otp

def reconstruct_color_id(share1, share2):
    return cv2.bitwise_xor(share1, share2)

def verify_integrity(reconstructed_img, original_seal):
    current_seal = hashlib.sha256(reconstructed_img.tobytes()).hexdigest()
    return current_seal == original_seal

def get_random_cover():
    cover_dir = "assets/covers/"
    if not os.path.exists(cover_dir): os.makedirs(cover_dir)
    covers = [f for f in os.listdir(cover_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return os.path.join(cover_dir, random.choice(covers)) if covers else None