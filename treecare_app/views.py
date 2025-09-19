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
# Import hàm predict từ ONNX
# =========================
from .convert_to_nano import predict


def analyze_image(file_path):
    try:
        with Image.open(file_path) as im:
            im = im.convert("RGB")

        class_name, score = predict(im)  # gọi ONNX predict

        if score < 0.4:
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

            # Phân tích ảnh ngay sau khi upload
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

        return Response({
            "status": "success",
            "tree_id": tree.id,
            "species": tree.Species,
            "disease": tree.Disease,
            "result": tree.Result,
            "image_url": request.build_absolute_uri(tree.UploadImage.url)
        }, status=status.HTTP_200_OK)
