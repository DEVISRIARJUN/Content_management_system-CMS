from rest_framework import serializers
from .models import MediaAsset
from apps.accounts.serializers import UserSerializer


class MediaAssetSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    formatted_size = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = [
            'id', 'title', 'file', 'file_url', 'file_type', 'file_size_bytes',
            'formatted_size', 'mime_type', 'alt_text', 's3_key', 'uploaded_by',
            'created_at'
        ]
        read_only_fields = ['file_size_bytes', 'mime_type', 's3_key', 'created_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file:
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return ''

    def get_formatted_size(self, obj):
        bytes_val = obj.file_size_bytes
        if bytes_val < 1024:
            return f"{bytes_val} B"
        elif bytes_val < 1024 * 1024:
            return f"{bytes_val / 1024:.1f} KB"
        return f"{bytes_val / (1024 * 1024):.2f} MB"
