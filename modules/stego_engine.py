import cv2
import numpy as np

def embed_lsb(share_array, cover_path, output_path, passcode):
    # Load and resize using NEAREST to prevent pixel blurring
    cover = cv2.imread(cover_path)
    h, w = share_array.shape[:2]
    cv_resized = cv2.resize(cover, (w, h), interpolation=cv2.INTER_NEAREST)
    
    # Advanced 4-Bit Plane Concealment
    stego_img = (cv_resized & 0xF0) | (share_array >> 4)
    
    # Save as LOSSLESS PNG
    cv2.imwrite(output_path, stego_img, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    return output_path

def extract_lsb(stego_path, passcode):
    stego = cv2.imread(stego_path)
    if stego is None: return None
    # Extract bottom 4 bits and restore intensity
    return (stego & 0x0F) << 4