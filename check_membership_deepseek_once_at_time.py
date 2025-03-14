# import cv2
# import easyocr
# import re
# import sqlite3
# from datetime import datetime, timedelta
# import time

# # Initialize OCR reader
# reader = easyocr.Reader(['fr'])

# # Database setup
# conn = sqlite3.connect('parking.db')
# c = conn.cursor()

# # Global variables
# last_processed = None
# cooldown = 2  # seconds
# current_status = "Ready for scan"
# current_plate = ""

# def preprocess_image(image):
#     """Optimized preprocessing for single plate capture"""
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
#     contrast = clahe.apply(gray)
#     denoised = cv2.fastNlMeansDenoising(contrast, h=10)
#     _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#     return thresh

# def read_license_plate(image):
#     """Single plate processing with strict validation"""
#     processed = preprocess_image(image)
#     results = reader.readtext(processed, paragraph=True, detail=0)
    
#     french_pattern = re.compile(r'^[A-Z]{2}-?\d{3}-?[A-Z]{2}$')
#     replacements = [('O','0'),('Q','0'),('I','1'),(' ',''),('-','')]
    
#     for text in results:
#         clean_text = text.upper()
#         for wrong, right in replacements:
#             clean_text = clean_text.replace(wrong, right)
        
#         if len(clean_text) == 7 and french_pattern.match(
#             f"{clean_text[:2]}-{clean_text[2:5]}-{clean_text[5:]}"
#         ):
#             return clean_text
#     return None

# def check_membership(plate):
#     """Database check with timestamp"""
#     today = datetime.now().date()
#     c.execute('''SELECT end_date FROM vehicles 
#               WHERE license_plate = ? AND end_date >= ?''',
#               (plate, today))
#     return c.fetchone() is not None

# def check_membership(plate):
#     """Database check with timestamp"""
#     today = datetime.now().date()
#     c.execute('''SELECT end_date FROM vehicles 
#               WHERE license_plate = ? AND end_date >= ?''',
#               (plate, today))
#     return c.fetchone() is not None

# def format_plate(plate):
#     """Format plate number as AA-000-BB for display"""
#     if not plate or len(plate) != 7:
#         return ""
#     return f"{plate[:2]}-{plate[2:5]}-{plate[5:]}"

# def format_cooldown(seconds):
#     """Visual feedback for scan timing"""
#     return f"Next scan in: {max(0, seconds):.1f}s"

# # Initialize camera
# cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # Process timing
#     now = time.time()
#     elapsed = now - (last_processed or 0)
    
#     # Process frame if cooldown expired
#     if elapsed >= cooldown:
#         plate = read_license_plate(frame)
#         if plate:
#             current_plate = plate
#             current_status = "GRANTED" if check_membership(plate) else "DENIED"
#             last_processed = now
#         else:
#             current_status = "No plate detected"
#             last_processed = now  # Reset timer even on failure
    
#     # Display information
#     timer_text = format_cooldown(cooldown - elapsed) if last_processed else "Ready"
#     color = (0, 255, 0) if elapsed >= cooldown else (0, 0, 255)
    
#     cv2.putText(frame, f"Status: {current_status}", (20, 50), 
#                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
#     cv2.putText(frame, f"Plate: {format_plate(current_plate)}", (20, 100), 
#                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
#     cv2.putText(frame, timer_text, (20, 150), 
#                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
#     # Visual scan indicator
#     cv2.rectangle(frame, (520, 300), (760, 400), color, 3)
#     cv2.putText(frame, "ALIGN PLATE HERE", (450, 280), 
#                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
#     cv2.imshow('Parking Control System', frame)
    
#     # Exit on ESC
#     if cv2.waitKey(1) == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()
# conn.close()

######new
# import cv2
# import easyocr
# import re
# import sqlite3
# from datetime import datetime
# import numpy as np
# import time

# # Initialize OCR reader
# reader = easyocr.Reader(['fr'])

# # Database setup
# conn = sqlite3.connect('parking.db')
# c = conn.cursor()

# # Configuration
# ROI = (400, 200, 900, 500)
# PLATE_PATTERN = re.compile(r'^[A-Z]{2}-?\d{3}-?[A-Z]{2}$')
# LOCK_RESULT_TIME = 5  # Seconds to display result before exit

# def validate_plate(text):
#     """Validate and format French license plate"""
#     replacements = [
#         ('O', '0'), ('Q', '0'), ('I', '1'),
#         ('Z', '2'), ('S', '5'), ('B', '8'),
#         (' ', ''), ('-', '')
#     ]
    
#     clean_text = text.upper()
#     for wrong, right in replacements:
#         clean_text = clean_text.replace(wrong, right)
    
#     if len(clean_text) == 7 and PLATE_PATTERN.match(
#         f"{clean_text[:2]}-{clean_text[2:5]}-{clean_text[5:]}"
#     ):
#         return clean_text
#     return None

# def check_membership(plate):
#     today = datetime.now().strftime('%Y-%m-%d')
#     c.execute('''SELECT end_date FROM vehicles 
#               WHERE license_plate = ? 
#               AND start_date <= ? 
#               AND end_date >= ?''',
#               (plate, today, today))
#     return c.fetchone() is not None

# def process_frame(frame):
#     """Process frame and return plate if valid"""
#     roi = frame[ROI[1]:ROI[3], ROI[0]:ROI[2]]
#     gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
#     _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#     results = reader.readtext(thresh, detail=0, paragraph=True)
    
#     for text in results:
#         # plate = validate_plate(text)
#         if plate:
#             return plate
#     return None

# # Initialize camera
# cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# final_result = None
# start_time = time.time()

# while True:
#     ret, frame = cap.read()
#     if not ret or (final_result and time.time() - start_time > LOCK_RESULT_TIME):
#         break

#     # Process frame only if no result yet
#     if not final_result:
#         plate = process_frame(frame)
#         if plate:
#             final_result = {
#                 'plate': plate,
#                 'status': 'GRANTED' if check_membership(plate) else 'DENIED',
#                 'time': time.time()
#             }
#             start_time = time.time()  # Reset timer

#     # Display results
#     cv2.rectangle(frame, (ROI[0], ROI[1]), (ROI[2], ROI[3]), (0, 255, 0), 2)
    
#     if final_result:
#         display_text = [
#             f"Plate: {final_result['plate'][:2]}-{final_result['plate'][2:5]}-{final_result['plate'][5:]}",
#             f"Status: {final_result['status']}",
#             f"Closing in {LOCK_RESULT_TIME - int(time.time() - start_time)}s"
#         ]
#         color = (0, 255, 0) if final_result['status'] == 'GRANTED' else (0, 0, 255)
#     else:
#         display_text = ["Scanning..."]
#         color = (255, 255, 255)

#     y_offset = 100
#     for text in display_text:
#         cv2.putText(frame, text, (50, y_offset), 
#                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
#         y_offset += 50

#     cv2.imshow('License Plate Recognition', frame)
    
#     if cv2.waitKey(1) == 27:  # ESC to exit
#         break

# cap.release()
# cv2.destroyAllWindows()
# conn.close()

import cv2
import easyocr
import re
import sqlite3
import numpy as np
import time
from datetime import datetime

# Initialize OCR reader
reader = easyocr.Reader(['fr'])

# Database setup
conn = sqlite3.connect('parking.db')
c = conn.cursor()

# Create vehicles table
c.execute('''CREATE TABLE IF NOT EXISTS vehicles (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             license_plate TEXT UNIQUE,
             owner_name TEXT,
             start_date DATE,
             end_date DATE)''')
conn.commit()

# Configuration
FIXED_ROI = (400, 200, 900, 500)  # Fixed detection area (x1, y1, x2, y2)
LOCK_RESULT_TIME = 5  # Seconds to display result

def preprocess_image(image):
    """Enhanced preprocessing to distinguish B/E characters"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Increased contrast for better character separation
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)
    
    # Morphological closing to close gaps in characters
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    closed = cv2.morphologyEx(contrast, cv2.MORPH_CLOSE, kernel)
    
    # Adaptive thresholding with optimized parameters
    return cv2.adaptiveThreshold(closed, 255, 
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY_INV, 31, 4)

def validate_plate(text):
    """Enhanced validation with B/E specific checks"""
    replacements = [
        ('O', '0'), ('Q', '0'), ('I', '1'),
        ('Z', '2'), ('S', '5'), ('8', 'B'),  # Prioritize B over 8
        (' ', ''), ('-', ''), ('É', 'E'), ('È', 'E')
    ]
    
    # First pass cleaning
    clean_text = text.upper()
    for wrong, right in replacements:
        clean_text = clean_text.replace(wrong, right)
    
    # Special handling for last two characters
    if len(clean_text) == 7:
        # Convert ambiguous E to B in position 5-6
        prefix = clean_text[:5]
        suffix = clean_text[5:].replace('E', 'B')
        clean_text = prefix + suffix
    
    # Final validation
    if re.match(r'^[A-Z]{2}\d{3}[A-Z]{2}$', clean_text):
        return clean_text
    return None

def check_membership(plate):
    """Check database for active membership"""
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('''SELECT end_date FROM vehicles 
              WHERE license_plate = ? 
              AND start_date <= ? 
              AND end_date >= ?''',
              (plate, today, today))
    return c.fetchone() is not None

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

final_result = None
start_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret or (final_result and time.time() - start_time > LOCK_RESULT_TIME):
        break

    # Draw fixed green detection area
    x1, y1, x2, y2 = FIXED_ROI
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    # Process only the fixed ROI area
    roi = frame[y1:y2, x1:x2]
    
    if not final_result:
        processed = preprocess_image(roi)
        results = reader.readtext(processed, detail=0, paragraph=True)
        
        for text in results:
            plate = validate_plate(text)
            if plate:
                final_result = {
                    'plate': plate,
                    'status': 'GRANTED' if check_membership(plate) else 'DENIED',
                    'time': time.time()
                }
                start_time = time.time()
                break

    # Display results
    if final_result:
        display_text = [
            f"Plate: {final_result['plate'][:2]}-{final_result['plate'][2:5]}-{final_result['plate'][5:]}",
            f"Status: {final_result['status']}",
            f"Closing in {LOCK_RESULT_TIME - int(time.time() - start_time)}s"
        ]
        color = (0, 255, 0) if final_result['status'] == 'GRANTED' else (0, 0, 255)
    else:
        display_text = ["Align plate in green area"]
        color = (255, 255, 255)

    y_offset = 50
    for text in display_text:
        cv2.putText(frame, text, (50, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        y_offset += 40

    cv2.imshow('License Plate Recognition', frame)
    
    if cv2.waitKey(1) == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
conn.close()