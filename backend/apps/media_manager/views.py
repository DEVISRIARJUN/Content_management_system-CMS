import uuid
import os
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from .models import MediaAsset
from .serializers import MediaAssetSerializer


class MediaAssetViewSet(viewsets.ModelViewSet):
    queryset = MediaAsset.objects.all()
    serializer_class = MediaAssetSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = MediaAsset.objects.select_related('uploaded_by').all()
        
        file_type = self.request.query_params.get('type')
        if file_type and file_type != 'all':
            qs = qs.filter(file_type=file_type)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(alt_text__icontains=search))

        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(uploaded_by=user)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def presigned_url(self, request):
        """
        Generates S3 Presigned URL for direct browser-to-S3 uploads.
        If S3 is not configured in .env, provides a direct local upload URL fallback.
        """
        filename = request.data.get('filename', 'upload.bin')
        content_type = request.data.get('content_type', 'application/octet-stream')
        s3_bucket = os.getenv('AWS_STORAGE_BUCKET_NAME')

        key = f"media/{uuid.uuid4().hex[:8]}_{filename}"

        if s3_bucket:
            # When AWS credentials are set, this uses boto3
            try:
                import boto3
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
                )
                presigned_url = s3_client.generate_presigned_url(
                    'put_object',
                    Params={'Bucket': s3_bucket, 'Key': key, 'ContentType': content_type},
                    ExpiresIn=300
                )
                return Response({
                    "upload_mode": "s3",
                    "url": presigned_url,
                    "key": key,
                    "final_url": f"https://{s3_bucket}.s3.amazonaws.com/{key}"
                })
            except Exception as e:
                pass

        # Local storage fallback
        return Response({
            "upload_mode": "local",
            "url": "/api/media/",
            "key": key,
            "message": "Use standard POST multipart/form-data to /api/media/"
        })
