from rest_framework import serializers
from .models import Tree

class TreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tree
        fields = '__all__'

    def get_upload_image(self, obj):
        request = self.context.get('request')
        if obj.UploadImage and request:
            return request.build_absolute_uri(obj.UploadImage.url)
        return None