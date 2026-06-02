import os
import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor
from yt_dlp import YoutubeDL
from time import sleep
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# === TELEGRAM BOT ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Telegram bot token from environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! I am your YouTube downloader bot. Send me a YouTube link!')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if 'youtube' in url or 'youtu.be' in url:
        await update.message.reply_text('Downloading...please wait!')
        download_video(url, get_ydl_opts())
        await update.message.reply_text('Download complete!')
    else:
        await update.message.reply_text('Please send a valid YouTube URL')

def start_telegram_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler(None, handle_message))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# === YouTube Functions ===
def auto_update_ytdlp():
    subprocess.run(["python3", "-m", "pip", "install", "--upgrade", "yt-dlp"], stdout=subprocess.DEVNULL)

def get_ydl_opts():
    return {
        'quiet': True,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'best',
        'ignoreerrors': True,
    }

def download_video(url, ydl_opts):
    try:
        os.makedirs('downloads', exist_ok=True)
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print("Error downloading", url, ":", e)

# === Main ===
def main():
    # Start Flask web server (for Render health check)
    threading.Thread(target=run_web, daemon=True).start()
    
    # Auto-update yt-dlp
    auto_update_ytdlp()
    
    # Start Telegram bot
    print("Starting Telegram bot...")
    start_telegram_bot()

if __name__ == '__main__':
    main()
