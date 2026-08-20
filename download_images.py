import os
import requests
import time

SOURCE_OWNER = "ShahGCreator"
SOURCE_REPO = "icon"
SOURCE_PATH = "PNG"
BRANCH = "main"

IMAGE_DIR = "PNG"
os.makedirs(IMAGE_DIR, exist_ok=True)

HEADERS = {"Accept": "application/vnd.github.v3+json"}

def get_all_png_files():
    files = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{SOURCE_OWNER}/{SOURCE_REPO}/contents/{SOURCE_PATH}?ref={BRANCH}&page={page}&per_page=100"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            print(f"⚠️ API warning: {resp.status_code} - continuing with partial list")
            break
        data = resp.json()
        if not data:
            break
        for item in data:
            if item["name"].endswith(".png"):
                files.append(item["download_url"])
        if len(data) < 100:
            break
        page += 1
        time.sleep(0.5)
    return files

def download_file(url, filename):
    filepath = os.path.join(IMAGE_DIR, filename)
    
    if os.path.exists(filepath):
        print(f"⏭️ Skipped (already exists): {filename}")
        return False
    
    try:
        resp = requests.get(url, stream=True)
        if resp.status_code == 200:
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)
            print(f"✅ Downloaded: {filename}")
            return True
    except Exception as e:
        print(f"❌ Failed: {filename} - {e}")
    return False

def main():
    print("🚀 Checking for new PNGs from ShahGCreator/icon...")
    
    remote_files = get_all_png_files()
    total_remote = len(remote_files)
    print(f"📁 Remote: {total_remote} PNG files found")
    
    local_files = [f for f in os.listdir(IMAGE_DIR) if f.endswith(".png")]
    print(f"📂 Local: {len(local_files)} PNG files already exist")
    
    new_files = 0
    batch_size = 100
    total_downloaded = 0
    
    for idx, url in enumerate(remote_files, start=1):
        filename = url.split("/")[-1]
        if download_file(url, filename):
            new_files += 1
            total_downloaded += 1
        
        # প্রতি ১০০টি ফাইল ডাউনলোডের পর স্ট্যাটাস দেখাও
        if idx % batch_size == 0 or idx == total_remote:
            print(f"📊 Progress: {idx}/{total_remote} files processed, {total_downloaded} new files downloaded so far")
        
        time.sleep(0.2)  # রেট লিমিট এড়াতে
    
    print(f"🎉 Done! Total {new_files} new files downloaded")
    if new_files == 0:
        print("✅ No new files to download. Repository is up to date.")

if __name__ == "__main__":
    main()
