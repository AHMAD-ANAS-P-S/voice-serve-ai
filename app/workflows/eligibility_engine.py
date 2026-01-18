# app/workflows/eligibility_engine.py

def check_eligibility(data: dict) -> bool:
    """
    Simple rule-based eligibility check (DEMO SAFE)
    """
    if not data.get("aadhaar"):
        return False

    if not data.get("bank"):
        return False

    if not data.get("ifsc"):
        return False

    return True


def eligibility_response(language: str, eligible: bool) -> str:
    """
    Explain eligibility result in simple words
    """
    if language == "ta":
        if eligible:
            return "நீங்கள் PM-Kisan திட்டத்திற்கு தகுதியுடையவர்."
        else:
            return "தேவையான விவரங்கள் இல்லை. நீங்கள் தற்போது தகுதி பெறவில்லை."

    # English
    if eligible:
        return "You are eligible for the PM-Kisan scheme."
    else:
        return "Some required details are missing. You are not eligible yet."
