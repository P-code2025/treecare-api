from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from pathlib import Path
from .models import Tree
from .serializer import TreeSerializer
import traceback
import os
from PIL import Image
import io

# =========================
# Giới hạn thread để giảm RAM/CPU
# =========================
os.environ["OMP_NUM_THREADS"] = "1"
try:
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
except ImportError:
    pass

# =========================
# PRELOAD YOLO MODEL
# =========================
from ultralytics import YOLO

MODEL_PATH = Path(settings.BASE_DIR) / 'best_nano.pt' 

try:
    print("🔄 Loading YOLO model at server start...")
    yolo_model = YOLO(str(MODEL_PATH))
    print(f"✅ Model loaded from {MODEL_PATH}")
except Exception as e:
    print("❌ Error loading YOLO model:", e)
    yolo_model = None


def get_model():
    if yolo_model is None:
        raise RuntimeError("YOLO model not loaded")
    return yolo_model


def analyze_image(file_path):
    try:
        # Resize ảnh trước khi predict
        with Image.open(file_path) as im:
            im = im.convert("RGB")
            im.thumbnail((320, 320))  # ép kích thước tối đa 320px
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=90)
            buf.seek(0)

        model = get_model()
        results = model(buf, imgsz=320, conf=0.25, device='cpu', half=False, verbose=False)

        if not results:
            return "Unknown", "Unknown"

        r = results[0]
        probs = r.probs
        if probs is None:
            return "Unknown", "Unknown"

        top_class_id = probs.top1
        class_name = model.names[top_class_id]
        confidence = probs.top1conf
        if confidence < 0.4:
            return "Can't identify", "Please try again with a clearer image"

        if '__' in class_name:
            species, disease = class_name.split('__')
            species = species.replace('_', ' ')
            disease = disease.replace('_', ' ').title()
        else:
            species, disease = class_name, "Unknown"

        return species, disease
    except Exception as e:
        traceback.print_exc()
        return "Analysis failed", str(e)


class UploadImageView(APIView):
    def post(self, request):
        try:
            image = request.FILES.get('image')
            if not image:
                return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

            if not image.content_type.startswith('image/'):
                return Response({'error': 'File must be an image'}, status=status.HTTP_400_BAD_REQUEST)

            tree = Tree.objects.create(
                UploadImage=image,
                Species="Unknown",
                Disease="Unknown",
                Result="Processing"
            )

            # Analyze the image ngay sau khi upload
            species, disease = analyze_image(tree.UploadImage.path)
            tree.Species = species
            tree.Disease = disease
            tree.Result = f"{species} - {disease}" if disease != "Unknown" else species
            tree.save()

            return Response({
                "status": "success",
                "tree_id": tree.id,
                "filename": tree.UploadImage.name,
                "species": tree.Species,
                "disease": tree.Disease,
                "result": tree.Result,
                "image_url": request.build_absolute_uri(tree.UploadImage.url),
                "message": "Image uploaded and analyzed"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': f'Upload failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TreeResultView(APIView):
    def get(self, request, tree_id):
        try:
            tree = Tree.objects.get(id=tree_id)
        except Tree.DoesNotExist:
            return Response({"error": "Tree not found"}, status=status.HTTP_404_NOT_FOUND)

        # ❌ Bỏ re-analyze để GET không chạy YOLO nữa
        return Response({
            "status": "success",
            "tree_id": tree.id,
            "species": tree.Species,
            "disease": tree.Disease,
            "result": tree.Result,
            "image_url": request.build_absolute_uri(tree.UploadImage.url)
        }, status=status.HTTP_200_OK)
