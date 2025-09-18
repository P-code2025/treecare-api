import os
import shutil
import requests
from zipfile import ZipFile

# Thay FILE_ID bằng ID thật của file trên Google Drive
FILE_ID = "1N_BK2z7pIOFFG08nz4EBLU0ugd3BYLg4"
ZIP_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

def download_and_extract(url):
    zip_path = "all_images.zip"
    tmp_dir = "tmp_images"

    # 1. Tải file zip
    print("📥 Đang tải ảnh từ Google Drive...")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(zip_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    # 2. Giải nén tạm
    print("📂 Đang giải nén tạm...")
    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(tmp_dir)
    os.remove(zip_path)

    # 3. Tạo thư mục đích
    os.makedirs("media/tree_images", exist_ok=True)
    os.makedirs("tree_images", exist_ok=True)

    # 4. Phân loại ảnh
    for file in os.listdir(tmp_dir):
        src = os.path.join(tmp_dir, file)
        if os.path.isfile(src):
            # Ví dụ: nếu tên file chứa 'fruit' thì cho vào tree_images, còn lại vào media/tree_images
            if "fruit" in file.lower():
                shutil.move(src, os.path.join("tree_images", file))
            else:
                shutil.move(src, os.path.join("media/tree_images", file))

    # 5. Xóa thư mục tạm
    shutil.rmtree(tmp_dir)
    print("✅ Hoàn tất phân loại ảnh!")

if __name__ == "__main__":
    download_and_extract(ZIP_URL)