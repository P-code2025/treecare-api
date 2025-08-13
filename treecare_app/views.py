from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import FileSystemStorage
from ultralytics import YOLO
import os
from .models import Tree
from .serializer import TreeSerializer

model = YOLO('/Users/quanganh/Documents/django/treecarebe/treecare/best.pt')

class UploadImageView(APIView):
    def post(self, request):
        if 'image' not in request.FILES:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        image = request.FILES['image']
        
        if not image.content_type.startswith('image/'):
            return Response({'error': 'File must be an image'}, status=status.HTTP_400_BAD_REQUEST)
        
        tree = Tree.objects.create(
            UploadImage=image,
            Result="Analyzing..."
        )
        
        # Analyze immediately using YOLO classification model
        species_result = "Unknown"
        disease_result = "Unknown"
        
        try:
            file_path = tree.UploadImage.path
            results = model(file_path)
            
            if results and len(results) > 0:
                # Get the first (and likely only) result
                r = results[0]
                probs = r.probs  # probabilities
                
                if probs is not None:
                    # Get top prediction
                    top_class_id = probs.top1
                    class_name = model.names[top_class_id]
                    confidence = probs.top1conf.item()
                    
                    # Split the class name by '__' to get species and disease
                    if '__' in class_name:
                        species, disease = class_name.split('__')
                        # Replace underscores with spaces for better readability
                        species = species.replace('_', ' ')
                        disease = disease.replace('_', ' ')
                        # Capitalize first letter of each word in disease
                        disease = disease.title()
                        species_result = species
                        disease_result = disease
                    else:
                        # Fallback if no '__' separator
                        species_result = class_name
                    
                else:
                    species_result = "No probabilities found"
            else:
                species_result = "No results to process"
                    
        except Exception as e:
            species_result = f"Analysis failed: {str(e)}"
            import traceback
            traceback.print_exc()
        
        # Update the tree with both species and disease results
        # tree.Result = f"Species: {species_result} | Disease: {disease_result}"  # Remove this line
        
        # Safely update Species and Disease fields if they exist
        try:
            if hasattr(tree, 'Species'):
                tree.Species = species_result
                print(f"Saving Species: {species_result}")
            if hasattr(tree, 'Disease'):
                tree.Disease = disease_result
                print(f"Saving Disease: {disease_result}")
        except AttributeError:
            # If fields don't exist, just save the Result
            print("Species or Disease fields not found")
            pass
            
        tree.save()
        print(f"After save - Species: {tree.Species}, Disease: {tree.Disease}")
        
        return Response({
            "status": "success",
            "tree_id": tree.id,
            "filename": tree.UploadImage.name,
            "species": tree.Species if tree.Species else "Unknown",
            "disease": tree.Disease if tree.Disease else "Unknown",
            "image_url": tree.UploadImage.url,
            "message": "Image uploaded and analyzed"
        }, status=status.HTTP_201_CREATED)

class TreeResultView(APIView):
    
    def get(self, request, tree_id):
        try:
            tree = Tree.objects.get(id=tree_id)
        except Tree.DoesNotExist:
            return Response({"error": "Tree not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if not tree.UploadImage:
            return Response({"error": "No image found for this tree"}, status=status.HTTP_404_NOT_FOUND)
        
        # If the stored result indicates a failure, re-analyze
        if tree.Result.startswith("Analysis failed") or tree.Result == "Pending analysis":
            try:
                file_path = tree.UploadImage.path
                results = model(file_path)
                
                print(f"Re-analyzing image for tree {tree_id}")
                
                if results and len(results) > 0:
                    # Get the first (and likely only) result
                    r = results[0]
                    probs = r.probs  # probabilities
                    
                    if probs is not None:
                        # Get top prediction
                        top_class_id = probs.top1
                        class_name = model.names[top_class_id]
                        confidence = probs.top1conf.item()
                        
                        # Split the class name by '__' to get species and disease
                        if '__' in class_name:
                            species, disease = class_name.split('__')
                            # Replace underscores with spaces for better readability
                            species = species.replace('_', ' ')
                            disease = disease.replace('_', ' ')
                            # Capitalize first letter of each word in disease
                            disease = disease.title()
                            species_result = species
                            disease_result = disease
                        else:
                            # Fallback if no '__' separator
                            species_result = class_name
                            disease_result = "Unknown"
                        
                        print(f"Re-analysis - Species: {species_result}, Disease: {disease_result}")
                        
                        # Safely update Species and Disease fields if they exist
                        try:
                            if hasattr(tree, 'Species'):
                                tree.Species = species_result
                            if hasattr(tree, 'Disease'):
                                tree.Disease = disease_result
                        except AttributeError:
                            # If fields don't exist, just save the Result
                            pass
                            
                        tree.save()
                    else:
                        tree.Result = "No probabilities found"
                        tree.save()
                else:
                    tree.Result = "No results to process"
                    tree.save()
                    
            except Exception as e:
                tree.Result = f"Re-analysis failed: {str(e)}"
                tree.save()
                print(f"Re-analysis error: {e}")
                import traceback
                traceback.print_exc()
        
        return Response({
            "status": "success",
            "species": tree.Species if tree.Species else "Unknown",
            "disease": tree.Disease if tree.Disease else "Unknown",
            "image_url": tree.UploadImage.url,
            "tree_id": tree.id
        }, status=status.HTTP_200_OK)

