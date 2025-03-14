import datetime

# Sample membership database.
# Each entry maps a license plate (in uppercase) to its membership expiration date.
monthly_memberships = {
    "ABC-123": datetime.date(2025, 12, 31),
    "XYZ-789": datetime.date(2024, 6, 30),
    "LMN-456": datetime.date(2022, 12, 31),  # This membership is expired if today's date is after 2022-12-31.
}

def check_membership(license_plate):
    """
    Checks whether the given license plate has an active monthly membership.
    
    Parameters:
        license_plate (str): The vehicle's license plate number.
    
    Returns:
        bool: True if the vehicle has an active membership, False otherwise.
    """
    # Standardize the input to uppercase and remove any extra whitespace.
    license_plate = license_plate.upper().strip()
    
    # Look up the license plate in the membership database.
    if license_plate in monthly_memberships:
        expiration_date = monthly_memberships[license_plate]
        today = datetime.date.today()
        # The membership is active if today's date is on or before the expiration date.
        if today <= expiration_date:
            return True
    return False

def simulate_license_plate_scan():
    """
    Simulates the scanning of a vehicle's license plate.
    In a real system, this function could integrate with a camera and an OCR system.
    
    Returns:
        str: The scanned (or entered) license plate.
    """
    # For simulation purposes, we simply prompt the user.
    return input("Please scan or enter your vehicle's license plate: ")

def main():
    # Simulate the scanning of the license plate.
    license_plate = simulate_license_plate_scan()
    
    # Check if the license plate has an active monthly membership.
    if check_membership(license_plate):
        print(f"Access granted: The membership for {license_plate} is active.")
    else:
        print(f"Access denied: No active membership found for {license_plate}.")

if __name__ == "__main__":
    main()
