from datetime import datetime, timedelta


def schedule_pm_kisan_reminder(receipt_id: str) -> dict:
    """
    MOCK reminder scheduling (demo only)
    """

    reminder_date = datetime.now() + timedelta(days=120)  # 4 months

    return {
        "receipt_id": receipt_id,
        "reminder_date": reminder_date.strftime("%Y-%m-%d"),
        "status": "scheduled"
    }
