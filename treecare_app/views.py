from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import FileSystemStorage
from ultralytics import YOLO
import os
from .models import Tree
from .serializer import TreeSerializer

# model = YOLO('sex_model.pt')

class UploadImageView(APIView):
    def post(self, request):
        if 'image' not in request.FILES:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        image = request.FILES['image']
        
        if not image.content_type.startswith('image/'):
            return Response({'error': 'File must be an image'}, status=status.HTTP_400_BAD_REQUEST)
        
        fs = FileSystemStorage(location='media/')
        filename = fs.save(image.name, image)
        
        tree = Tree.objects.create(
            UploadImage=image,
            Result="Pending analysis" 
        )
        
        return Response({
            "status": "success",
            "filename": filename,
            "tree_id": tree.id,
            "message": "Image uploaded successfully"
        }, status=status.HTTP_201_CREATED)

class TreeResultView(APIView):
    
    def get(self, request, tree_id):
        try:
            tree = Tree.objects.get(id=tree_id)
        except Tree.DoesNotExist:
            return Response({"error": "Tree not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if not tree.UploadImage:
            return Response({"error": "No image found for this tree"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "status": "success",
            "result": tree.Result,
            "image_url": tree.UploadImage.url,
            "tree_id": tree.id
        }, status=status.HTTP_200_OK)

