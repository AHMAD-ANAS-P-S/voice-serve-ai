def missing_fields(farmer_data: dict) -> list:
    required = ["name", "aadhaar", "bank", "ifsc", "mobile", "land"]
    missing = []

    for field in required:
        if not farmer_data.get(field):
            missing.append(field)

    return missing
