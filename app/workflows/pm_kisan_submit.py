import requests
from app.config import settings

def submit_pm_kisan(data: dict):
    response = requests.post(
        f"{settings.MOCK_PORTAL_URL}/submit",
        data=data
    )
    return response.json()
