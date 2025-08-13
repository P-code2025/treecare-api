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
        prediction_text = "Analysis failed"
        try:
            file_path = tree.UploadImage.path
            results = model(file_path)
            
            print(f"YOLO classification results: {results}")
            
            if results and len(results) > 0:
                for r in results:
                    probs = r.probs  # probabilities
                    if probs is not None:
                        top_class_id = probs.top1
                        class_name = model.names[top_class_id]
                        confidence = probs.top1conf.item()  # Use top1conf instead of probs[top_class_id].item()
                        
                        prediction_text = f"{class_name} (Confidence: {confidence:.3f})"
                        print(f"Class: {class_name}, Confidence: {confidence}")
                        break
                    else:
                        prediction_text = "No probabilities found"
                        print("No probabilities attribute found")
                else:
                    prediction_text = "No results to process"
                    
        except Exception as e:
            prediction_text = f"Analysis failed: {str(e)}"
            print(f"YOLO classification error: {e}")
            import traceback
            traceback.print_exc()
        
        # Persist result
        tree.Result = prediction_text
        tree.save()
        
        return Response({
            "status": "success",
            "tree_id": tree.id,
            "filename": tree.UploadImage.name,
            "result": tree.Result,
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
                    for r in results:
                        probs = r.probs  # probabilities
                        if probs is not None:
                            top_class_id = probs.top1
                            class_name = model.names[top_class_id]
                            confidence = probs.top1conf.item()
                            
                            prediction_text = f"{class_name} (Confidence: {confidence:.3f})"
                            print(f"Re-analysis - Class: {class_name}, Confidence: {confidence}")
                            
                            # Update the stored result
                            tree.Result = prediction_text
                            tree.save()
                            break
                        else:
                            prediction_text = "No probabilities found"
                            tree.Result = prediction_text
                            tree.save()
                    else:
                        prediction_text = "No results to process"
                        tree.Result = prediction_text
                        tree.save()
                else:
                    prediction_text = "No results to process"
                    tree.Result = prediction_text
                    tree.save()
                    
            except Exception as e:
                prediction_text = f"Re-analysis failed: {str(e)}"
                tree.Result = prediction_text
                tree.save()
                print(f"Re-analysis error: {e}")
                import traceback
                traceback.print_exc()
        
        return Response({
            "status": "success",
            "result": tree.Result,
            "image_url": tree.UploadImage.url,
            "tree_id": tree.id
        }, status=status.HTTP_200_OK)

