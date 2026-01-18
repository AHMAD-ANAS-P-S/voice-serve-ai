
# 🚀 How to Run Voice Serve AI

This system contains:
1. **AI Backend + Web Frontend** (Single command)
2. **Telegram Bot** (Optional)

---

## 1. Setup

First, install all dependencies:
```bash
pip install -r requirements.txt
```
*Note: Ensure `ffmpeg` is installed on your system for audio processing.*

---

## 2. Run Website & API (Main)

Run this single command to start the entire system (Frontend, Backend, and Mock Gov Portal):

```bash
python run_system.py
```

*   **Website**: Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
*   **API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
*   **Mock Gov Portal**: [http://127.0.0.1:9000](http://127.0.0.1:9000)

---

## 3. Run Telegram Bot (Optional)

1.  Open Telegram and search for **@BotFather**.
2.  Send `/newbot` and follow instructions to get a **Bot Token**.
3.  Add the token to your `.env` file:
    ```
    TELEGRAM_BOT_TOKEN=your_token_here_12345
    ```
4.  Run the bot script in a **new terminal**:
    ```bash
    python scripts/telegram_bot.py
    ```

Now you can speak to your bot on Telegram!
