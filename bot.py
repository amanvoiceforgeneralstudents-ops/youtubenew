import os
import argparse
import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from time import sleep
from flask import Flask

# === 🌐 Dummy Web Server for Render ===
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# === 🔄 Auto-update yt-dlp ===
def auto_update_ytdlp():
    print("🔄 Checking for yt-dlp update...")
    subprocess.run(["python3", "-m", "pip", "install", "--upgrade", "yt-dlp"], stdout=subprocess.DEVNULL)

# === 🧪 Validate URL ===
def is_valid_url(url):
    try:
        with YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
        return True
    except Exception:
        return False

# === 📤 Download Function ===
def download_video(url, ydl_opts, max_retries=3):
    for attempt in range(max_retries):
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return
        except DownloadError as e:
            sleep(2 ** attempt)

# === 🧠 Main ===
def main():
    # 1. Start Web Server in background
    threading.Thread(target=run_web, daemon=True).start()
    
    # 2. Main Logic
    auto_update_ytdlp()
    
    # Read from links.txt automatically instead of input()
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

        print(f"🚀 Starting download of {len(urls)} items...")
        with ThreadPoolExecutor(max_workers=2) as executor:
            for url in urls:
                executor.submit(download_video, url, ydl_opts)
        print("\n✅ Processing complete!")
    
    # Keep script running
    while True:
        sleep(60)

if __name__ == '__main__':
    main()
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            log_downloaded(url)
            return
        except DownloadError as e:
            print(f"⚠️ Attempt {attempt + 1} failed for {url}: {e}")
            sleep(2 ** attempt)
    log_failed(url)
    print(f"❌ Skipped after {max_retries} failed attempts: {url}")

# === 📄 Logging ===
def log_downloaded(url):
    with open('downloaded.txt', 'a') as f:
        f.write(url + '\n')

def log_failed(url):
    with open('failed.txt', 'a') as f:
        f.write(url + '\n')

# === 📁 Load URLs ===
def load_urls(file_path=None):
    urls = []
    if file_path:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    else:
        print("🔗 Enter YouTube URLs (type 'done' to finish):")
        while True:
            url = input("> ").strip()
            if url.lower() == 'done':
                break
            if url:
                urls.append(url)
    return urls

# === 🧵 Threaded Download ===
def threaded_download(urls, ydl_opts, threads):
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(download_video, url, ydl_opts): url for url in urls}
        for future in as_completed(futures):
            future.result()

# === 🧠 Main ===
def main():
    auto_update_ytdlp()

    parser = argparse.ArgumentParser(description="YouTube Downloader PRO")
    parser.add_argument('--audio', action='store_true', help='Download audio only (MP3)')
    parser.add_argument('--file', type=str, help='Path to file containing URLs')
    parser.add_argument('--dir', type=str, default='downloads', help='Output directory')
    parser.add_argument('--threads', type=int, default=2, help='Number of parallel downloads')
    args = parser.parse_args()

    urls = load_urls(args.file)
    if not urls:
        print("❌ No URLs provided.")
        return

    urls = [url for url in urls if is_valid_url(url)]
    if not urls:
        print("❌ All URLs invalid.")
        return

    os.makedirs(args.dir, exist_ok=True)

    output_template = os.path.join(args.dir, '%(uploader)s/%(playlist_title)s/%(title)s.%(ext)s')

    ydl_opts = {
        'quiet': True,
        'progress_hooks': [progress_hook],
        'outtmpl': output_template,
        'merge_output_format': 'mp4',
        'download_archive': 'archive.txt',
        'ignoreerrors': True,
        'noplaylist': False,
        'format': 'bestaudio/best' if args.audio else 'bestvideo+bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if args.audio else []
    }

    print(f"🚀 Starting download of {len(urls)} item(s) using {args.threads} thread(s)...")
    threaded_download(urls, ydl_opts, args.threads)
    print("\n✅ All downloads complete!")

if __name__ == '__main__':
    main()
