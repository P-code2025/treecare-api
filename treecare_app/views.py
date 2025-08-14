from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ultralytics import YOLO
from django.conf import settings
from pathlib import Path
from .models import Tree
from .serializer import TreeSerializer
import traceback
import os


# Use relative path from BASE_DIR instead of hardcoded absolute path
model_path = Path(settings.BASE_DIR) / 'best.pt'
model = YOLO(str(model_path))

def analyze_image(file_path):
    """Run YOLO classification and return (species, disease) tuple."""
    try:
        results = model(file_path)
        if not results:
            return "Unknown", "Unknown"

        r = results[0]
        probs = r.probs

        if probs is None:
            return "Unknown", "Unknown"

        top_class_id = probs.top1
        class_name = model.names[top_class_id]

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

            # Create the tree record first
            tree = Tree.objects.create(
                UploadImage=image,
                Species="Unknown",
                Disease="Unknown",
                Result="Processing"  # Set initial result
            )

            # Analyze the image
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
                "image_url": tree.UploadImage.url,
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

        # If no species/disease found or analysis failed → re-analyze
        if tree.Species in ["Unknown", "Analysis failed"]:
            try:
                species, disease = analyze_image(tree.UploadImage.path)
                tree.Species = species
                tree.Disease = disease
                tree.Result = f"{species} - {disease}" if disease != "Unknown" else species
                tree.save()
            except Exception as e:
                return Response({
                    "error": f"Re-analysis failed: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "status": "success",
            "tree_id": tree.id,
            "species": tree.Species,
            "disease": tree.Disease,
            "result": tree.Result,
            "image_url": tree.UploadImage.url
        }, status=status.HTTP_200_OK)