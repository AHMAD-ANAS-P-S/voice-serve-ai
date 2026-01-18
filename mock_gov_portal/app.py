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
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Seva Setu | Unified Welfare Portal</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #6366f1;
                --bg: #0f172a;
                --card: rgba(255, 255, 255, 0.05);
                --card-border: rgba(255, 255, 255, 0.1);
            }
            body { 
                background: radial-gradient(circle at top right, #1e1b4b, #0f172a); 
                color: white; font-family: 'Outfit', sans-serif;
                margin: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh;
            }
            .container { text-align: center; max-width: 900px; padding: 20px; }
            h1 { font-size: 3rem; margin-bottom: 10px; background: linear-gradient(to right, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            p { color: #94a3b8; font-size: 1.1rem; margin-bottom: 40px; }
            .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; width: 100%; }
            .card {
                background: var(--card); border: 1px solid var(--card-border); padding: 40px 20px; border-radius: 24px;
                text-decoration: none; color: white; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                backdrop-filter: blur(10px); display: flex; flex-direction: column; align-items: center; gap: 15px;
            }
            .card:hover { transform: translateY(-10px); background: rgba(255,255,255,0.08); border-color: var(--primary); box-shadow: 0 20px 40px -10px rgba(99, 102, 241, 0.3); }
            .card i { font-size: 3.5rem; margin-bottom: 10px; }
            .card h3 { margin: 0; font-size: 1.25rem; }
            .card span { font-size: 0.85rem; color: #64748b; }
            @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Unified Welfare Dashboard</h1>
            <p>Empowering citizens through seamless AI-assisted service delivery.</p>
            <div class="grid">
                <a href="pm-kisan" class="card">
                    <i>🚜</i>
                    <h3>PM-Kisan</h3>
                    <span>Farmer Support Scheme</span>
                </a>
                <a href="scholarship" class="card">
                    <i>🎓</i>
                    <h3>NSP Portal</h3>
                    <span>National Scholarship</span>
                </a>
                <a href="hospital" class="card">
                    <i>🏥</i>
                    <h3>E-Booking</h3>
                    <span>Hospital Appointment</span>
                </a>
            </div>
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
