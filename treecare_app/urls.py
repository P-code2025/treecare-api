from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.UploadImageView.as_view(), name='upload_image'),
    path('result/<int:tree_id>/', views.TreeResultView.as_view(), name='tree_result'),
]