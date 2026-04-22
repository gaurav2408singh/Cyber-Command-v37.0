import cv2
import os
from deepface import DeepFace
from fpdf import FPDF
import datetime

def perform_ai_face_match(id_image_path, live_frame):
    """Deep Learning Biometric Verification"""
    try:
        temp_live = "data/temp_live.jpg"
        cv2.imwrite(temp_live, live_frame)
        
        result = DeepFace.verify(
            img1_path = id_image_path, 
            img2_path = temp_live, 
            model_name = "VGG-Face",
            enforce_detection = False
        )
        
        if os.path.exists(temp_live): os.remove(temp_live)
        
        match_found = result['verified']
        score = round((1 - result['distance']) * 100, 2)
        return match_found, score
    except Exception as e:
        print(f"AI Error: {e}")
        return False, 0

def generate_forensic_report(status, match_val, audit_log_text):
    """Generates the PDF and handles Unicode symbol conflicts"""
    try:
        # CLEANUP: Replace the '▶' symbol with '>' so the PDF font doesn't crash
        clean_log = audit_log_text.replace("▶", ">")
        
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "GOVERNMENT IDENTITY AUTHENTICATION REPORT", ln=True, align='C')
        pdf.ln(5)
        
        # Metadata
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Date/Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.cell(0, 10, f"AI Biometric Score: {match_val}%", ln=True)
        pdf.cell(0, 10, f"Final Status: {status}", ln=True)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Forensic Audit Trail Log:", ln=True)
        
        # Content
        pdf.set_font("Courier", size=9) # Use Courier for a 'terminal' look in PDF
        pdf.multi_cell(0, 5, clean_log)
        
        filename = f"Forensic_Report_{datetime.datetime.now().strftime('%H%M%S')}.pdf"
        pdf.output(filename)
        return filename
    except Exception as e:
        raise Exception(f"PDF Engine Error: {str(e)}")