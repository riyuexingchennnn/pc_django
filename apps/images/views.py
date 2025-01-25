from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.conf import settings
import os
import logging

logger = logging.getLogger("django")


class ImageUploadView(APIView):
    def post(self, request):
        # 检查是否有文件在请求中
        image = request.FILES.get("image")
        if not image:
            return Response(
                {"message": "No image file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 保存图片到指定目录 (MEDIA_ROOT)
        try:
            save_path = os.path.join(settings.MEDIA_ROOT, image.name)
            with default_storage.open(save_path, "wb+") as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

            logger.info(f"Image uploaded successfully: {image.name}")
            # 返回图片的访问路径
            image_url = f"{settings.MEDIA_URL}{image.name}"
            return Response(
                {"message": "Image uploaded successfully.", "url": image_url},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            return Response(
                {"message": "Failed to upload image."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
