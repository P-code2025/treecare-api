import os
import shutil
import requests
from zipfile import ZipFile

FILE_ID = "1N_BK2z7pIOFFG08nz4EBLU0ugd3BYLg4"
ZIP_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

UPLOAD_DIR = os.path.join("media", "tree_images")

def safe_filename(path_dir, filename):
    import uuid
    name, ext = os.path.splitext(filename)
    candidate = filename
    while os.path.exists(os.path.join(path_dir, candidate)):
        candidate = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
    return candidate

def download_and_extract(url):
    zip_path = "all_images.zip"
    tmp_dir = "tmp_images"

    print("📥 Đang tải ảnh từ Google Drive...")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(zip_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    print("📂 Đang giải nén tạm...")
    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(tmp_dir)
    os.remove(zip_path)

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    count_files = 0
    for file in os.listdir(tmp_dir):
        src = os.path.join(tmp_dir, file)
        if not os.path.isfile(src):
            continue
        lower = file.lower()
        if not (lower.endswith(".jpg") or lower.endswith(".jpeg") or lower.endswith(".png")):
            continue
        target_name = safe_filename(UPLOAD_DIR, file)
        shutil.move(src, os.path.join(UPLOAD_DIR, target_name))
        count_files += 1

    shutil.rmtree(tmp_dir)
    print(f"✅ Hoàn tất: {count_files} ảnh đã được lưu vào {UPLOAD_DIR}")

if __name__ == "__main__":
    download_and_extract(ZIP_URL)
