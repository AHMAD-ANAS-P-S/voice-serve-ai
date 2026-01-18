
import logging
import os
import requests
import json
from dotenv import load_dotenv
from app.config import settings
from telegram import Update, Voice
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Load Env
load_dotenv()
TOKEN = settings.TELEGRAM_BOT_TOKEN
API_URL = settings.AI_BACKEND_URL

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Welcome to SEVA-SETU AI! (Voice Serve AI)\n\n"
        "speak in Tamil or English. I can help with:\n"
        "🏥 Healthcare (சுகாதாரம்)\n"
        "📚 Education (கல்வி)\n"
        "🚜 Governance - PM Kisan (நிர்வாகம்)\n\n"
        "🎤 Send a Voice Note (குரல்)\n"
        "🖼️ Send Aadhaar Image (ஆதார்)\n"
        "📝 Send Text (உரை)"
    )
    await update.message.reply_text(welcome_text)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    await update.message.chat.send_action(action="typing")
    
    try:
        # Use multipart/form-data for consistency with backend
        files = {'text': (None, text)}
        response = requests.post(API_URL, data={"text": text, "user_id": user_id})
        data = response.json()
        
        reply_text = data.get("response", "No response from server.")
        voice_url = data.get("voice_url")
        
        # Reply with Text
        await update.message.reply_text(reply_text)
        
        # Reply with Voice (If generated)
        if voice_url:
            # Handle both local path and remote URL
            if voice_url.startswith("http"):
                v_resp = requests.get(voice_url)
                if v_resp.status_code == 200:
                    await update.message.reply_voice(voice=v_resp.content)
            else:
                # Local path case
                clean_path = voice_url.lstrip("/") 
                if os.path.exists(clean_path):
                    with open(clean_path, 'rb') as v_file:
                        await update.message.reply_voice(voice=v_file)

    except Exception as e:
        await update.message.reply_text(f"Connection Error: {e}\nMake sure run_system.py is running!")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    voice_file = await update.message.voice.get_file()
    
    # Save as .ogg (Telegram default) - Faster Whisper handles this
    voice_path = f"telegram_voice_{user_id}.ogg"
    await voice_file.download_to_drive(voice_path)
    
    await update.message.chat.send_action(action="record_voice")

    try:
        with open(voice_path, 'rb') as audio_data:
            files = {"audio": ("voice.ogg", audio_data, "audio/ogg")}
            response = requests.post(
                API_URL, 
                data={"user_id": user_id},
                files=files
            )
            
        data = response.json()
        reply_text = data.get("response", "No voice response.")
        voice_url = data.get("voice_url")

        await update.message.reply_text(reply_text)
        
        if voice_url:
            if voice_url.startswith("http"):
                v_resp = requests.get(voice_url)
                if v_resp.status_code == 200:
                    await update.message.reply_voice(voice=v_resp.content)
            else:
                clean_path = voice_url.lstrip("/")
                if os.path.exists(clean_path):
                    with open(clean_path, 'rb') as v_file:
                        await update.message.reply_voice(voice=v_file)

    except Exception as e:
        await update.message.reply_text(f"Voice Processing Error: {e}")
    finally:
        if os.path.exists(voice_path):
            os.remove(voice_path)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    # Get largest photo
    photo_file = await update.message.photo[-1].get_file()
    photo_path = f"telegram_img_{user_id}.jpg"
    await photo_file.download_to_drive(photo_path)
    
    await update.message.reply_text("📥 Image received. Processing Aadhaar...")

    try:
        with open(photo_path, 'rb') as img_data:
            files = {"image": ("aadhaar.jpg", img_data, "image/jpeg")}
            response = requests.post(
                API_URL, 
                data={"user_id": user_id},
                files=files
            )
        
        data = response.json()
        reply_text = data.get("response", "Could not process image.")
        voice_url = data.get("voice_url")

        await update.message.reply_text(reply_text)
        
        if voice_url:
            if voice_url.startswith("http"):
                v_resp = requests.get(voice_url)
                if v_resp.status_code == 200:
                    await update.message.reply_voice(voice=v_resp.content)
            else:
                clean_path = voice_url.lstrip("/")
                if os.path.exists(clean_path):
                    with open(clean_path, 'rb') as v_file:
                        await update.message.reply_voice(voice=v_file)

    except Exception as e:
        await update.message.reply_text(f"Image Error: {e}")
    finally:
        if os.path.exists(photo_path):
            os.remove(photo_path)

if __name__ == '__main__':
    if not TOKEN:
        print("❌ CRITICAL ERROR: TELEGRAM_BOT_TOKEN not found in .env")
        print("Please add TELEGRAM_BOT_TOKEN=... to your .env file.")
        exit(1)
        
    print("🚀 SEVA-SETU Telegram Bot is starting...")
    print("🔗 Connecting to Backend at:", API_URL)
    
    # Use a longer timeout for polling and requests
    application = ApplicationBuilder().token(TOKEN).read_timeout(30).write_timeout(30).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    
    print("✅ Bot is online! Press Ctrl+C to stop.")
    try:
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        if "Conflict" in str(e):
            print("❌ ERROR: Another bot instance is running. Kill it first!")
        else:
            print(f"❌ ERROR: {e}")
