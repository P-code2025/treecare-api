"""
URL configuration for treecare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app import views
    2. Add a URL to urlpatterns:  path('', views.Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from treecare_app.models import Tree
from treecare_app.serializer import TreeSerializer

def home(request):
    # Lấy toàn bộ bản ghi Tree từ DB
    trees = Tree.objects.all()
    serializer = TreeSerializer(trees, many=True)
    return JsonResponse(serializer.data, safe=False)

urlpatterns = [
    path('', home),  # Truy cập gốc sẽ trả về danh sách cây
    path('admin/', admin.site.urls),
    path('tree/', include('treecare_app.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)