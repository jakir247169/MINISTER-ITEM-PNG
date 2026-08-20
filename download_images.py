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
            print(f"API error: {resp.status_code}")
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
    try:
        resp = requests.get(url, stream=True)
        if resp.status_code == 200:
            filepath = os.path.join(IMAGE_DIR, filename)
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)
            print(f"✅ Downloaded: {filename}")
            return True
    except Exception as e:
        print(f"❌ Failed: {filename} - {e}")
    return False

def main():
    print("🚀 Downloading PNGs from ShahGCreator/icon...")
    files = get_all_png_files()
    print(f"📁 Total {len(files)} PNG files found")
    success = 0
    for url in files:
        filename = url.split("/")[-1]
        if download_file(url, filename):
            success += 1
        time.sleep(0.2)
    print(f"🎉 Done! {success} files downloaded")

if __name__ == "__main__":
    main()