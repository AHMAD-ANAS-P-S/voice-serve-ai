from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uuid
import json
import os

# Create a child app that can be mounted
portal_app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
DATA_FILE = os.path.join(BASE_DIR, "data.json")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

portal_app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def get_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
             return {}
    return {}

def save_data(data):
    current = get_data()
    current.update(data)
    with open(DATA_FILE, "w") as f:
        json.dump(current, f)

@portal_app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head><title>Seva Setu | Welfare Portal</title><link rel="stylesheet" href="static/style.css"></head>
    <body style="text-align:center; padding-top:50px;">
        <h1>Seva Setu - Unified Welfare Portal</h1>
        <div style="display:flex; justify-content:center; gap:20px; margin-top:30px;">
            <a href="pm-kisan" style="padding:20px; border:2px solid green; border-radius:10px; text-decoration:none; color:black;">🚜 PM-Kisan</a>
            <a href="scholarship" style="padding:20px; border:2px solid blue; border-radius:10px; text-decoration:none; color:black;">🎓 Scholarship</a>
            <a href="hospital" style="padding:20px; border:2px solid red; border-radius:10px; text-decoration:none; color:black;">🏥 Hospital Booking</a>
        </div>
    </body>
    </html>
    """

@portal_app.get("/pm-kisan", response_class=HTMLResponse)
def kisan():
    with open(os.path.join(TEMPLATES_DIR, "pm_kisan_form.html"), "r", encoding="utf-8") as f:
        return f.read()

@portal_app.get("/scholarship", response_class=HTMLResponse)
def scholarship():
    with open(os.path.join(TEMPLATES_DIR, "scholarship_form.html"), "r", encoding="utf-8") as f:
        return f.read()

@portal_app.get("/hospital", response_class=HTMLResponse)
def hospital():
    with open(os.path.join(TEMPLATES_DIR, "hospital_form.html"), "r", encoding="utf-8") as f:
        return f.read()

@portal_app.get("/get_current_data")
def get_current_data():
    return get_data()

@portal_app.post("/update_state")
async def update_state(request: Request):
    data = await request.json()
    save_data(data)
    return {"status": "success"}

@portal_app.get("/reset")
def reset():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    return {"status": "reset", "message": "Portal Reset!"}

@portal_app.post("/submit")
def submit(
    name: str = Form(...),
    aadhaar: str = Form(...),
    mobile: str = Form(None),
    scheme: str = Form("General")
):
    receipt_id = f"{scheme[:3].upper()}-" + str(uuid.uuid4())[:8].upper()
    save_data({"submitted": True, "receipt_id": receipt_id, "active_scheme": scheme})
    return {
        "status": "Submitted Successfully",
        "scheme": scheme,
        "receipt_id": receipt_id
    }
