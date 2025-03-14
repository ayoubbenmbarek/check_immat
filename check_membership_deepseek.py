import sqlite3
from datetime import datetime
import cv2
import easyocr
import re

# Initialize OCR reader
reader = easyocr.Reader(['fr'])  # Using French language model

# Database setup
conn = sqlite3.connect('parking.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS vehicles (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             license_plate TEXT UNIQUE,
             owner_name TEXT,
             start_date DATE,
             end_date DATE)''')
conn.commit()

def add_sample_data():
    """Add sample data for testing"""
    # Inserting French format plates (stored without hyphens)
    samples = [
        ('AB123CD', 'Marie Dupont', '2024-01-01', '2024-12-31'),
        ('XY789ZZ', 'Jean Martin', '2024-03-01', '2024-06-30'),
        ('TR654WW', 'Sophie Leroy', '2024-05-01', '2024-05-31'),
        ('AA000BB', 'Ayoub Ben', '2024-05-01', '2024-05-31'),
        ('FA235FB', 'Olfa Baby', '2024-05-01', '2025-05-31'),
        ('AA123AA', 'Olfa Baby', '2024-05-01', '2025-05-31')
        
    ]
    for plate, name, start, end in samples:
        c.execute("INSERT OR IGNORE INTO vehicles VALUES (NULL, ?, ?, ?, ?)",
                  (plate, name, start, end))
    conn.commit()

def preprocess_image(image):
    """Enhanced image preprocessing for French plates"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # Additional processing for French plate contrast
    thresh = cv2.adaptiveThreshold(blur, 255, 
                                  cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY_INV, 11, 2)
    print(thresh)
    return thresh

def read_license_plate(image):
    """Process image and read French license plates"""
    processed = preprocess_image(image)
    results = reader.readtext(processed, paragraph=True)
    
    french_plate_pattern = re.compile(r'^[A-Z]{2}-?\d{3}-?[A-Z]{2}$')
    plates = []
    
    for detection in results:
        text = detection[1].upper().replace(' ', '')
        # Clean and validate French plate format
        clean_text = re.sub(r'[^A-Z0-9]', '', text)
        
        # Validate using French plate pattern
        if french_plate_pattern.match(text) or (
            len(clean_text) == 7 and 
            re.match(r'^[A-Z]{2}\d{3}[A-Z]{2}$', clean_text)
        ):
            # Format as AA-000-BB if valid
            formatted = f"{clean_text[:2]}-{clean_text[2:5]}-{clean_text[5:]}"
            plates.append(formatted.replace('-', ''))  # Store without hyphens
    print(plates, "here plates")
    return list(set(plates))  # Remove duplicates

def check_membership(license_plate):
    """Check if license plate has active membership"""
    today = datetime.today().strftime('%Y-%m-%d')
    c.execute('''SELECT * FROM vehicles 
              WHERE license_plate = ? 
              AND start_date <= ? 
              AND end_date >= ?''', 
              (license_plate, today, today))
    return c.fetchone() is not None

def main():
    add_sample_data()
    
    # Load test image (replace with camera input)
    image = cv2.imread('images/car.jpg')
    
    plates = read_license_plate(image)
    print(plates)
    
    if not plates:
        print("No valid French license plate detected")
        return
    
    for plate in plates:
        if check_membership(plate):
            print(f"Vehicle {format_plate(plate)} is authorized. Access granted!")
            return
    
    print(f"Vehicle {format_plate(plate)} not authorized. Access denied.")

def format_plate(plate):
    """Format plate number as AA-000-BB for display"""
    return f"{plate[:2]}-{plate[2:5]}-{plate[5:]}" if len(plate) ==7 else plate

if __name__ == "__main__":
    main()
    conn.close()
