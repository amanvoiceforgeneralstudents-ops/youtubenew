import os
import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor
from yt_dlp import YoutubeDL
from time import sleep
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def auto_update_ytdlp():
    subprocess.run(["python3", "-m", "pip", "install", "--upgrade", "yt-dlp"], stdout=subprocess.DEVNULL)

def is_valid_url(url):
    try:
        with YoutubeDL({'quiet': True}) as ydl:
            ydl.extract_info(url, download=False)
        return True
    except Exception:
        return False

def download_video(url, ydl_opts):
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print("Error downloading", url, ":", e)

def main():
    threading.Thread(target=run_web, daemon=True).start()
    auto_update_ytdlp()
    
    if os.path.exists('links.txt'):
        with open('links.txt', 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        urls = [url for url in urls if is_valid_url(url)]
        os.makedirs('downloads', exist_ok=True)

        ydl_opts = {
            'quiet': True,
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'format': 'best',
            'ignoreerrors': True,
        }

        print("Starting download of", len(urls), "items...")
        with ThreadPoolExecutor(max_workers=2) as executor:
            for url in urls:
                executor.submit(download_video, url, ydl_opts)
        print("Processing complete!")
    
    while True:
        sleep(60)

if __name__ == '__main__':
    main()
