# 🚀 Hosting Guide: SEVA-SETU AI

This guide explains how to host your project so it can be used by anyone, anywhere.

## 1. Prerequisites
- A server or cloud account (AWS, DigitalOcean, Render, or Railway).
- Docker installed (Recommended for full project hosting).

## 2. Setting up Environment Variables
In your hosted environment (e.g., Render Dashboard), set these variables:
- `GEMINI_API_KEY`: Your Google AI Key.
- `OPENROUTER_API_KEY`: Your OpenRouter Key.
- `TELEGRAM_BOT_TOKEN`: From @BotFather.
- `AI_BACKEND_URL`: `https://your-public-url.com/api/v1/process`
- `MOCK_PORTAL_URL`: `https://your-public-url.com` (if running on same server).

## 3. Option A: Deployment with Docker (Easiest)
If your server supports Docker:
1. Upload the project folder to your server.
2. Run:
   ```bash
   docker-compose up --build -d
   ```
This will start both the AI Backend (with Web UI) and the Telegram Bot in the background.

## 4. Option B: Deployment on VPS (Manual)
1. **Clone project** and install requirements.
2. **Setup reverse proxy** (using Nginx) to point your domain to `localhost:8000`.
3. **Run background processes**:
   - Use `pm2` or `systemd` to keep `run_system.py` and `scripts/telegram_bot.py` running 24/7.

## 5. Option C: Quick Public Demo (Ngrok)
If you want to host it from your laptop temporarily for others to try:
1. Install [Ngrok](https://ngrok.com/).
2. Start your system: `python run_system.py`
3. Run in a new terminal: `ngrok http 8000`
4. Copy the `https://...` URL provided by Ngrok and update your `.env` `AI_BACKEND_URL`.

## 📌 Important for Public Use
- **CORS**: If hosting frontend and backend separately, ensure `app/main.py` has CORS middleware configured.
- **HTTPS**: Telegram bots require an HTTPS URL. Hosting services like Render or Ngrok provide this automatically.
