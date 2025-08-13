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
                res = results[0]
                print(f"Result type: {type(res)}")
                print(f"Result attributes: {dir(res)}")
                
                # Handle classification results
                if hasattr(res, 'probs') and res.probs is not None:
                    print(f"Classification probabilities: {res.probs}")
                    
                    # Get top prediction with confidence
                    if hasattr(res.probs, 'top1') and hasattr(res.probs, 'top1conf'):
                        # Newer ultralytics version
                        top_class = res.probs.top1
                        top_conf = res.probs.top1conf
                        prediction_text = f"Class {top_class} (Confidence: {top_conf:.2f})"
                        
                    elif hasattr(res.probs, 'cpu') and hasattr(res.probs, 'numpy'):
                        # Convert to numpy and get top prediction
                        probs_np = res.probs.cpu().numpy()
                        top_idx = probs_np.argmax()
                        top_conf = probs_np.max()
                        
                        # Get class name if available
                        names_map = getattr(res, 'names', {}) or {}
                        class_name = names_map.get(top_idx, f"Class {top_idx}")
                        
                        prediction_text = f"{class_name} (Confidence: {top_conf:.2f})"
                        
                    elif hasattr(res.probs, 'tolist'):
                        # Convert to list and get top prediction
                        probs_list = res.probs.tolist()
                        top_idx = probs_list.index(max(probs_list))
                        top_conf = max(probs_list)
                        
                        names_map = getattr(res, 'names', {}) or {}
                        class_name = names_map.get(top_idx, f"Class {top_idx}")
                        
                        prediction_text = f"{class_name} (Confidence: {top_conf:.2f})"
                        
                    else:
                        # Fallback
                        prediction_text = f"Classification result: {res.probs}"
                        
                else:
                    # Try to find probabilities in other attributes
                    for attr in ['prob', 'predictions', 'output']:
                        if hasattr(res, attr):
                            value = getattr(res, attr)
                            if value is not None:
                                print(f"Found {attr}: {value}")
                                prediction_text = f"Result from {attr}: {value}"
                                break
                    else:
                        prediction_text = f"Classification result: {str(res)[:200]}..."
                        
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
        
        return Response({
            "status": "success",
            "result": tree.Result,
            "image_url": tree.UploadImage.url,
            "tree_id": tree.id
        }, status=status.HTTP_200_OK)

