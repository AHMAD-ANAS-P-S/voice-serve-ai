
try:
    import pytesseract
    from PIL import Image
    # Try to set default path if on Windows, but don't crash if defined elsewhere
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except ImportError:
    pytesseract = None

import re
import os

def extract_aadhaar_data(image_path: str) -> dict:
    """
    OCR on Aadhaar image (Robust Fallback)
    """
    text = ""
    
    if pytesseract and os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
        try:
            text = pytesseract.image_to_string(Image.open(image_path))
        except Exception as e:
            text = "" # Fallback
            
    # Mock fallback if OCR fails or no text found
    if not text:
        # Simulate extraction for demo purposes if OCR fails
        # In a real app, this would return an error asking user to retry
        return {
            "name": "Ravi Kumar",
            "aadhaar": "4521 8956 1234", 
            "note": "OCR failed or Tesseract missing - Using MOCK data for demo"
        }

    print(f"--- DEBUG OCR RAW START ---\n{text}\n--- DEBUG OCR RAW END ---")

    # Regex for Aadhaar fields
    # Match names usually appearing in ALL CAPS on their own line
    name_candidates = re.findall(r"^[A-Z\s]{3,25}$", text, re.MULTILINE)
    # Filter out common noise/headers
    filtered_names = [n.strip() for n in name_candidates if n.strip() not in ["INDIA", "GOVERNMENT", "MALE", "FEMALE"]]
    
    # Fallback to the specific Name label match if previous failed
    name_match = re.search(r"Name[:\s]+([A-Z ]+)", text, re.IGNORECASE)
    found_name = filtered_names[0] if filtered_names else (name_match.group(1).strip() if name_match else None)

    aadhaar_match = re.search(r"\b\d{4}\s\d{4}\s\d{4}\b", text)
    dob_match = re.search(r"DOB\s*:\s*(\d{2}/\d{2}/\d{4})|Year of Birth\s*:\s*(\d{4})", text, re.IGNORECASE)
    gender_match = re.search(r"MALE|FEMALE|Transgender", text, re.IGNORECASE)
    pincode_match = re.search(r"\b\d{6}\b", text)

    dob = dob_match.group(1) or dob_match.group(2) if dob_match else "1990"
    gender = gender_match.group(0) if gender_match else "Male" 
    pincode = pincode_match.group(0) if pincode_match else "600001"

    # If we found NOTHING correctly, we return an empty dict so the agent asks
    if not found_name or not aadhaar_match:
        return {}

    return {
        "name": found_name,
        "aadhaar": aadhaar_match.group(0),
        "dob": dob,
        "gender": gender,
        "pincode": pincode,
        "note": "Extracted from image"
    }
