import os
import requests
import time
import subprocess

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
        
        # রেট লিমিট চেক
        if resp.status_code == 403 and 'rate limit' in resp.text.lower():
            print("⚠️ Rate limit hit. Waiting 60 seconds...")
            time.sleep(60)
            continue
        
        if resp.status_code != 200:
            print(f"⚠️ API error: {resp.status_code} - stopping")
            break
        
        data = resp.json()
        if not data:
            break
        
        for item in data:
            if item["name"].endswith(".png"):
                files.append(item["download_url"])
        
        # শেষ পেজ চেক
        if len(data) < 100:
            break
        
        page += 1
        time.sleep(0.5)  # রেট লিমিট এড়াতে
    
    return files

def download_file(url, filename):
    filepath = os.path.join(IMAGE_DIR, filename)
    if os.path.exists(filepath):
        return False
    try:
        resp = requests.get(url, stream=True, timeout=30)
        if resp.status_code == 200:
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"❌ Failed: {filename} - {e}")
    return False

def main():
    print("🚀 Downloading all PNGs from ShahGCreator/icon...")
    remote_files = get_all_png_files()
    total_remote = len(remote_files)
    print(f"📁 Total remote PNG files: {total_remote}")

    if total_remote == 0:
        print("❌ No files found. Check API or network.")
        return

    local_files = [f for f in os.listdir(IMAGE_DIR) if f.endswith(".png")]
    print(f"📂 Already downloaded: {len(local_files)} files")

    new_files = 0
    for url in remote_files:
        filename = url.split("/")[-1]
        if download_file(url, filename):
            new_files += 1
        # প্রতি ১০০ ফাইলে প্রগ্রেস দেখাও (ঐচ্ছিক)
        if new_files % 100 == 0:
            print(f"📥 Downloaded {new_files} files so far...")

    if new_files == 0:
        print("✅ No new files. Nothing to commit.")
        return

    print(f"📥 Downloaded {new_files} new files. Committing and pushing...")
    try:
        subprocess.run(["git", "config", "--global", "user.name", "jakir247169"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "smjakirh2471@gmail.com"], check=True)
        subprocess.run(["git", "add", "PNG/"], check=True)
        subprocess.run(["git", "commit", "-m", f"🔄 Added {new_files} new PNG images"], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"✅ Successfully pushed {new_files} new files to GitHub!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")

if __name__ == "__main__":
    main()
