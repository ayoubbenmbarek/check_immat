import sqlite3
from datetime import datetime
import cv2
import easyocr
import re
import threading

# Initialize OCR reader
reader = easyocr.Reader(['fr'])

# Database setup
conn = sqlite3.connect('parking.db')
c = conn.cursor()

# Global variables for thread-safe operations
latest_plate = None
access_status = ""
exit_signal = False

def database_operations():
    """Create tables if they don't exist"""
    c.execute('''CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_plate TEXT UNIQUE,
                owner_name TEXT,
                start_date DATE,
                end_date DATE)''')
    conn.commit()

def preprocess_image(image):
    """Enhanced preprocessing for real-time processing"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)
    resized = cv2.resize(contrast, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    denoised = cv2.fastNlMeansDenoising(resized, h=10)
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

# def read_license_plate(image):
#     """Process image and read license plate with error correction"""
#     processed = preprocess_image(image)
#     results = reader.readtext(processed, paragraph=False, detail=0)
    
#     french_pattern = re.compile(r'^[A-Z]{2}-?\d{3}-?[A-Z]{2}$', re.IGNORECASE)
#     plates = []
    
#     for text in results:
#         # Replace common OCR misreads
#         replacements = [
#             ('O', '0'), ('Q', '0'), ('I', '1'), 
#             ('Z', '2'), ('S', '5'), ('B', '8')
#         ]
#         clean_text = text.upper().replace(' ', '').replace('-', '')
#         for wrong, right in replacements:
#             clean_text = clean_text.replace(wrong, right)
        
#         # Validate format and length
#         if len(clean_text) == 7 and french_pattern.match(
#             f"{clean_text[:2]}-{clean_text[2:5]}-{clean_text[5:]}"
#         ):
#             plates.append(clean_text)
#     print(plates)
#     return plates
##############@old###################
def preprocess_image(image):
    """Enhanced preprocessing for reflective plates"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Handle reflective materials
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(16, 16))
    contrast = clahe.apply(gray)
    
    # Reduce glare
    blur = cv2.bilateralFilter(contrast, 11, 75, 75)
    
    # Dynamic thresholding
    thresh = cv2.adaptiveThreshold(blur, 255,
                                  cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY_INV, 31, 4)
    
    return thresh

def read_license_plate(image):
    """Modified to handle regulatory plate information"""
    processed = preprocess_image(image)
    results = reader.readtext(processed, paragraph=False, detail=0)
    
    print("Raw OCR Results:", results)  # Debugging line
    
    # Enhanced filtering for French plates
    plate_candidates = []
    french_pattern = re.compile(
        r'\b[A-Z]{2}[- ]?[0-9]{3}[- ]?[A-Z]{2}\b',
        re.IGNORECASE
    )
    
    for text in results:
        # Remove common non-plate text
        text = re.sub(r'(FaaS|Fabricauto|BREITAGNE|TPMR|TPPR)', '', text, flags=re.IGNORECASE)
        
        # OCR error correction
        replacements = [
            ('O', '0'), ('Q', '0'), ('I', '1'),
            ('Z', '2'), ('S', '5'), ('B', '8'),
            (' ', ''), ('-', '')
        ]
        
        clean_text = text.upper()
        for wrong, right in replacements:
            clean_text = clean_text.replace(wrong, right)
        
        # Validate plate structure
        if len(clean_text) == 7 and french_pattern.match(clean_text):
            plate_candidates.append(f"{clean_text[:2]}-{clean_text[2:5]}-{clean_text[5:]}")
    
    return plate_candidates

def check_membership(plate):
    """Check database for active membership"""
    today = datetime.today().strftime('%Y-%m-%d')
    c.execute('''SELECT * FROM vehicles 
              WHERE license_plate = ? 
              AND start_date <= ? 
              AND end_date >= ?''', 
              (plate, today, today))
    return c.fetchone() is not None

def processing_thread():
    """Separate thread for plate processing"""
    global latest_plate, access_status
    while not exit_signal:
        if current_frame is not None:
            plates = read_license_plate(current_frame)
            if plates:
                latest_plate = plates[0]  # Take first detected plate
                access_status = "GRANTED" if check_membership(latest_plate) else "DENIED"

def format_plate(plate):
    """Format plate for display"""
    return f"{plate[:2]}-{plate[2:5]}-{plate[5:]}" if plate else ""

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
# cap.set(cv2.CAP_PROP_EXPOSURE, 150)
# Better night performance
cap.set(cv2.CAP_PROP_EXPOSURE, -7)
# recognition distance
cap.set(cv2.CAP_PROP_ZOOM, 1.2)

# Start processing thread
current_frame = None
processing_thread = threading.Thread(target=processing_thread)
processing_thread.daemon = True
processing_thread.start()

# Main camera loop
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    current_frame = frame.copy()
    
    # Display results
    cv2.putText(frame, f"PLATE: {format_plate(latest_plate)}", 
               (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"ACCESS: {access_status}", 
               (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, 
               (0, 255, 0) if access_status == "GRANTED" else (0, 0, 255), 2)
    
    # Show frame
    cv2.imshow('License Plate Recognition', frame)
    
    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        exit_signal = True
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
conn.close()