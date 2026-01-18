
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.orchestrator.orchestrator import run_orchestrator
from mock_gov_portal.app import portal_app
import shutil
import os
import uuid
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Enable CORS for public hosting
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for audio playback
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount Mock Portal for unified hosting
app.mount("/portal", portal_app)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/v1/process")
async def process_input(
    text: str = Form(None),
    audio: UploadFile = File(None),
    image: UploadFile = File(None),
    user_id: str = Form("default")
):
    """
    Unified input: supports Text, Voice (Audio), and Image (Aadhaar).
    Multi-modal agent processing.
    """
    
    kwargs = {}
    
    # 1. Handle Audio Input (Voice)
    if audio:
        audio_path = f"static/input_{uuid.uuid4()}.mp3"
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        kwargs["audio_path"] = os.path.abspath(audio_path)
        
    # 2. Handle Image Input (Aadhaar OCR)
    if image:
        print(f"DEBUG: Received Image => {image.filename}")
        image_path = f"static/image_{uuid.uuid4()}.png"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        kwargs["aadhaar_image"] = os.path.abspath(image_path)

    # 3. Handle Text Input
    user_input = text or ""
    
    # 4. Run Orchestrator
    try:
        result = run_orchestrator(user_input, user_id=user_id, **kwargs)
    except Exception as e:
        import traceback
        print(f"CRITICAL ERROR in Orchestrator: {e}")
        traceback.print_exc()
        return {"response": "Sorry, an internal error occurred. Please try again.", "error": str(e)}
    
    # 5. Move generated audio to static for serving
    voice_url = None
    try:
        if result.get("voice_reply"):
            voice_filename = result["voice_reply"]
            # Ensure it's in static
            if not voice_filename.startswith("static/"):
                dest_path = f"static/{voice_filename}"
                if os.path.exists(voice_filename):
                    shutil.move(voice_filename, dest_path)
                voice_url = f"/static/{voice_filename}"
            else:
                voice_url = f"/{voice_filename}"
                
        # 6. RETURN (Clean result to ensure JSON serializability)
        return {
            "response": result.get("response"),
            "voice_url": voice_url,
            "next_steps": result.get("next_steps"),
            "domain": result.get("domain")
        }
    except Exception as e:
        print(f"Error serving response: {e}")
        return {"response": "Error preparing response.", "error": str(e)}

# Mount Frontend (Must be last to avoid masking API)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
