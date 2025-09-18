import os
import shutil
import requests
from zipfile import ZipFile
import django

# Khởi tạo Django ORM
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treecare.settings')
django.setup()

from treecare_app.models import Tree

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
    dest_dir = os.path.join("media", "tree_images")
    os.makedirs(dest_dir, exist_ok=True)

    # 4. Xóa dữ liệu cũ trong DB (nếu muốn làm mới mỗi lần deploy)
    Tree.objects.all().delete()

    # 5. Move ảnh và insert DB
    count = 0
    for file in os.listdir(tmp_dir):
        src = os.path.join(tmp_dir, file)
        if os.path.isfile(src):
            dest_path = os.path.join(dest_dir, file)
            shutil.move(src, dest_path)

            # Insert bản ghi DB
            Tree.objects.create(
                UploadImage=f"tree_images/{file}",  # đường dẫn tương đối
                Result=file,
                Species="Unknown",
                Disease="Unknown"
            )
            count += 1

    # 6. Xóa thư mục tạm
    shutil.rmtree(tmp_dir)
    print(f"✅ Hoàn tất: {count} ảnh đã được lưu vào media/tree_images và insert vào DB!")

if __name__ == "__main__":
    download_and_extract(ZIP_URL)