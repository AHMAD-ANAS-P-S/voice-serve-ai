def ask_aadhaar(language):
    if language == "ta":
        return {
            "response": (
                "PM-Kisan விண்ணப்பிக்க, உங்கள் ஆதார் அட்டை புகைப்படத்தை "
                "பதிவேற்றவும் அல்லது கேமராவில் காட்டவும்."
            ),
            "next_steps": ["upload_aadhaar"]
        }

    return {
        "response": (
            "To apply for PM-Kisan, please upload your Aadhaar card "
            "or capture it using your phone camera."
        ),
        "next_steps": ["upload_aadhaar"]
    }


def ask_bank(language):
    if language == "ta":
        return {
            "response": (
                "உங்கள் வங்கி கணக்கு எண்ணை சொல்லுங்கள். "
                "அல்லது பாஸ் புத்தகத்தை பதிவேற்றவும்."
            ),
            "next_steps": ["collect_bank"]
        }

    return {
        "response": (
            "Please say your bank account number, "
            "or upload a photo of your passbook."
        ),
        "next_steps": ["collect_bank"]
    }
