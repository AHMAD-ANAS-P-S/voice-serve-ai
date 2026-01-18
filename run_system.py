
import subprocess
import time
import sys
import os

def main():
    print("🚀 Starting SEVA-SETU Unified System...")
    
    # 1. Start the Unified Web Server (Frontend + AI API + Mock Portal)
    # Port is usually 8000 (standard) or from PORT env var for Render
    port = os.getenv("PORT", "8000")
    
    print(f"🌐 Starting Unified Web Server on Port {port}...")
    web_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app.main:app", 
        "--host", "0.0.0.0", "--port", port
    ])
    
    # Wait a bit for server to start
    time.sleep(5)
    
    # 2. Start the Telegram Bot in the same container
    print("🤖 Starting Telegram Bot side-by-side...")
    bot_process = subprocess.Popen([
        sys.executable, "scripts/telegram_bot.py"
    ])

    print("\n✅ SEVA-SETU is fully online!")
    
    try:
        # Keep the script running
        while True:
            if web_process.poll() is not None:
                print("❌ Web server crashed! Restarting...")
                web_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", port])
            
            if bot_process.poll() is not None:
                print("❌ Bot crashed! Restarting...")
                bot_process = subprocess.Popen([sys.executable, "scripts/telegram_bot.py"])
                
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Closing SEVA-SETU AI...")
        web_process.terminate()
        bot_process.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
