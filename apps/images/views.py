from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
import uuid
import io
import PIL
from qcloud_cos.cos_exception import CosClientError, CosServiceError
import base64
import urllib.parse
from django.core.exceptions import ObjectDoesNotExist

from .utils.ai import (
    content_filter,
    image_understanding,
    image_description,
    image_classification,
)
from .models import Image, ImageTag
from apps.accounts.models import User
from apps.utils.token_util import parse_token
from apps.utils.cos_util import (
    upload_image_cos,
    delete_image_cos,
    generate_image_url_cos,
)

# 设置日志
logger = logging.getLogger("django")

logger.info(r'''____    _           ____   _                       _ 
    |  _ \  (_)   ___   / ___| | |   ___    _   _    __| |
    | |_) | | |  / __| | |     | |  / _ \  | | | |  / _` |
    |  __/  | | | (__  | |___  | | | (_) | | |_| | | (_| |
    |_|     |_|  \___|  \____| |_|  \___/   \__,_|  \__,_|                                            
''')

# 上传图片视图
# 因为有众多步骤，所以导致上传图片相对较慢，一张图片大约20秒
# 如果是普通会员，没有图像描述功能，上传时间大约为10秒
class UploadImageView(APIView):
    def post(self, request, *args, **kwargs):
        
        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return Response(
                {"message": "token未提供"}, status=status.HTTP_400_BAD_REQUEST
            )
        payload = parse_token(token)
        if not payload:
            return Response(
                {"message": "token无效"}, status=status.HTTP_400_BAD_REQUEST
            )
        user_id = payload.get("user_id")

        # 获取文件和表单字段
        image_file = request.FILES.get("image")  # 获取图片文件(这个只能一张图片)
        time = request.data.get("time") or None  # 获取拍摄时间
        category = request.data.get("category") or "未分类"  # 获取分组
        position = request.data.get("position") or None  # 获取位置
        folder_url = request.data.get("folder_url") or "root/"  # 获取文件夹
        
        # 验证必填字段，图片文件
        if not image_file:
            return Response(
                {"success": False, "message": "没有图片文件"},
                status=status.HTTP_400_BAD_REQUEST,
            )  # 返回400错误，表示请求错误

        
        # print(type(payload_user_id))  # 输出 payload_user_id 的类型      int
        # print(type(user_id))  # 输出 user_id 的类型                      str

        # 首先检查用户存储空间是否足够
        user = User.objects.get(id=user_id)
        if (
            user.membership == "free"
            and user.used_space + image_file.size / 1024.0 / 1024.0 > 1024.0
        ):
            return Response(
                {
                    "success": False,
                    "message": "用户存储空间不足，请升级会员获取更多空间",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )  # 返回400错误，表示请求错误
        elif (
            user.membership == "silver"
            and user.used_space + image_file.size / 1024.0 / 1024.0 > 1024.0 * 5
        ):
            return Response(
                {
                    "success": False,
                    "message": "用户存储空间不足，请升级会员获取更多空间",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )  # 返回400错误，表示请求错误
        elif (
            user.membership == "gold"
            and user.used_space + image_file.size / 1024.0 / 1024.0 > 1024.0 * 10
        ):
            return Response(
                {"success": False, "message": "用户存储空间不足"},
                status=status.HTTP_400_BAD_REQUEST,
            )  # 返回400错误，表示请求错误

        # 生成一个唯一的UUID作为文件名
        image_id = str(uuid.uuid4())

        logger.debug(
            f"Metadata - user_id: {user_id}, time: {time}, category: {category}, position: {position}, name: {image_file.name}"
        )

        if image_file.size > 10 * 1024 * 1024:
            return Response(
                {"success": False, "message": "Image file size should not exceed 10MB"},
                status=status.HTTP_400_BAD_REQUEST,
            )  # 返回400错误，表示请求错误

        # 确保文件可以读取
        try:
            # 压缩图片并生成 Base64 编码
            def compress_image(
                image, target_size_kb=500, max_width=1024, max_height=1024
            ):
                img = PIL.Image.open(image)

                # 优化：调整图片分辨率（避免过大的图片尺寸）
                img.thumbnail((max_width, max_height))

                quality = 85  # 初始质量
                buffer = io.BytesIO()

                # print("压缩图片中...")

                # 压缩循环
                while True:
                    buffer.seek(0)
                    buffer.truncate(0)  # 清空缓冲区
                    img.save(buffer, format=img.format, quality=quality)  # 压缩图片
                    size_kb = buffer.tell() / 1024  # 当前图片大小 (KB)

                    # 如果文件小于目标大小或质量降到最低，则停止
                    if size_kb <= target_size_kb or quality <= 10:
                        break

                    # 降低质量继续压缩
                    quality -= 5

                buffer.seek(0)
                return base64.b64encode(buffer.read()).decode("utf-8"), size_kb

            # 生成 Base64 编码的压缩图片
            compressed_base64, compressed_size_kb = compress_image(
                image_file, target_size_kb=700
            )

            encoded_image = urllib.parse.quote_plus(
                compressed_base64
            )  # 这个函数用于将字符串进行 URL 编码

            result, reason = content_filter(encoded_image)  # 调用AI接口进行内容审核
            # print(result, reason)
            if result == "不合规":
                return Response(
                    {"success": False, "message": reason},
                    status=status.HTTP_400_BAD_REQUEST,
                )  # 返回400错误，表示请求错误

            tags = image_understanding(encoded_image)  # 调用AI接口进行图像理解
            # print(tags)

            description = "此图片没有描述"
            # 如果是普通会员
            if not User.objects.get(id=user_id).membership == "free":
                description = image_description(
                    compressed_base64
                )  # 调用AI接口进行图像描述
            # print(description)

            category = image_classification(compressed_base64)  # 调用AI接口进行图像分类
            # print(category)

        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return Response(
                {"success": False, "message": "Error reading file"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            ############################
            # 注意image_file.read()方法
            # 要用文件指针归零
            ############################
            image_file.seek(0)  # 将指针重置到文件的开头!!!
            response, image_url = upload_image_cos(
                image_id, image_file
            )  # 上传图片到腾讯云COS
            logger.info(f"COS Upload successful: {response}")

            image_instance = Image.objects.create(
                name=image_file.name,
                description=description,
                category=category,
                position=position,
                time=time,
                id=image_id,
                user_id=user_id,
                url=image_url,
                image_size=image_file.size / 1024.0 / 1024.0,
                folder_url=folder_url,
            )

            logger.info(f"Image instance created: {image_instance}")

            # 构建图像标签关系表
            # 如果标签不存在，则创建标签
            for tag_name in tags:
                ImageTag.objects.get_or_create(tag_name=tag_name, image_id=image_id)

            # 如果上传成功了，就要占用用户存储空间
            user.used_space += image_file.size / 1024.0 / 1024.0  # 单位为MB
            user.save()

            return Response(
                {
                    "success": True,
                    "message": "Image uploaded successfully",
                    "name": image_file.name,
                    "description": description,
                    "category": category,
                    "position": position,
                    "time": time,
                    "id": image_id,
                    "folder_url": folder_url,
                    "tags": tags,
                    "used_space": user.used_space,
                },
                status=status.HTTP_200_OK,
            )  # 返回状态码200，数据格式为JSON

        except (CosClientError, CosServiceError) as e:
            logger.error(f"Error uploading image: {e}")
            return Response(
                {"success": False, "message": "Image upload failed", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )  # 上传失败时，返回500状态码


# 删除图片视图
class DeleteImageView(APIView):
    def post(self, request, *args, **kwargs):

        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return Response(
                {"message": "token未提供"}, status=status.HTTP_400_BAD_REQUEST
            )
        payload = parse_token(token)
        if not payload:
            return Response(
                {"message": "token无效"}, status=status.HTTP_400_BAD_REQUEST
            )
        user_id = payload.get("user_id")
    
        # 获取图片ID
        image_id = request.data.get("image_id")

        user = User.objects.get(id=user_id)

        # 验证必填字段
        if not image_id:
            return Response(
                {"success": False, "message": "缺少image_id参数"},
                status=status.HTTP_400_BAD_REQUEST,  # 返回400错误，表示请求错误
            )

        try:
            # 查找数据库中的图片记录
            image_record = Image.objects.get(id=image_id)

            # 删除图像标签关系表中的记录
            ImageTag.objects.filter(image_id=image_id).delete()

            response = delete_image_cos(image_record.url)  # 删除图片到腾讯云COS
            logger.info(f"COS Delete successful: {response}")

            # 删除数据库中的记录
            image_record.delete()
            user.used_space -= image_record.image_size / 1024.0 / 1024.0  # 单位为MB
            user.save()

            return Response(
                {
                    "success": True,
                    "message": "Image deleted successfully",
                    "used_space": user.used_space,
                },
                status=status.HTTP_200_OK,  # 返回200，表示成功
            )
        except ObjectDoesNotExist:
            # 如果数据库中没有找到对应的记录
            return Response(
                {"success": False, "message": "Image not found in database"},
                status=status.HTTP_404_NOT_FOUND,  # 返回404，表示资源未找到
            )


# 修改图片视图
class UpdateImageView(APIView):
    def post(self, request, *args, **kwargs):

        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return Response(
                {"message": "token未提供"}, status=status.HTTP_400_BAD_REQUEST
            )
        payload = parse_token(token)
        if not payload:
            return Response(
                {"message": "token无效"}, status=status.HTTP_400_BAD_REQUEST
            )
        user_id = payload.get("user_id")
    
        # 获取图片ID（如果为空就是None，但是不会报错）
        image_id = request.data.get("image_id")
        name = request.data.get("name")
        description = request.data.get("description") 
        category = request.data.get("category")
        position = request.data.get("position")
        time = request.data.get("time")
        tags = request.data.get("tags")
        folder_url = request.data.get("folder_url")

        if not image_id:
            return Response(
                {"success": False, "message": "缺少image_id参数"},
                status=status.HTTP_400_BAD_REQUEST,  # 返回400错误，表示请求错误
            )
        try:
            # 查找数据库中的图片记录
            image_record = Image.objects.get(id=image_id)

            # 修改数据库中的记录
            image_record.category = category or image_record.category
            image_record.position = position or image_record.position
            image_record.time = time or image_record.time
            image_record.name = name or image_record.name
            image_record.description = description or image_record.description
            image_record.folder_url = folder_url or image_record.folder_url
            image_record.save()

            ImageTag.objects.filter(image_id=image_id).delete()
            for tag_name in tags:
                ImageTag.objects.create(tag_name=tag_name, image_id=image_id)

            return Response(
                {
                    "success": True,
                    "message": "Image updated successfully",
                    "name": image_record.name,
                    "description": image_record.description,
                    "category": image_record.category,
                    "position": image_record.position,
                    "time": image_record.time,
                    "tags": tags,
                    "folder_url": image_record.folder_url,
                },
                status=status.HTTP_200_OK,  # 返回200，表示成功
            )
        except ObjectDoesNotExist:
            # 如果数据库中没有找到对应的记录
            return Response(
                {"success": False, "message": "Image not found in database"},
                status=status.HTTP_404_NOT_FOUND,  # 返回404，表示资源未找到
            )


# 下载图片视图
class DownloadImageView(APIView):
    def post(self, request, *args, **kwargs):

        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return Response(
                {"message": "token未提供"}, status=status.HTTP_400_BAD_REQUEST
            )
        payload = parse_token(token)
        if not payload:
            return Response(
                {"message": "token无效"}, status=status.HTTP_400_BAD_REQUEST
            )
        user_id = payload.get("user_id")


        try:
            # 查找数据库中的图片记录
            image_records = Image.objects.filter(user_id=user_id)

            images = []

            # 下载图片
            for image_record in image_records:
                try:
                    # 设置URL过期时间（单位：秒）
                    expiration = 900  # 15分钟过期

                    presigned_url = generate_image_url_cos(image_record.url, expiration)

                    logger.debug(f"签名URL: {presigned_url}")

                    tags = ImageTag.objects.filter(
                        image_id=image_record.id
                    ).values_list("tag_name", flat=True)

                    image_info = {
                        "name": image_record.name,
                        "description": image_record.description,
                        "category": image_record.category,
                        "position": image_record.position,
                        "time": image_record.time,
                        "id": image_record.id,
                        "presigned_url": presigned_url,
                        "folder_url": image_record.folder_url,
                        "tags": tags,
                    }
                    images.append(image_info)

                except Exception as e:
                    logger.error(f"Error generating presigned URL: {e}")
                    return Response(
                        {
                            "success": False,
                            "message": f"Error generating presigned URL: {e}",
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,  # 返回505错误，表示服务器内部错误
                    )

            return Response(
                {"success": True, "message": images},
                status=status.HTTP_200_OK,  # 返回200，表示成功
            )
        except ObjectDoesNotExist:
            # 如果数据库中没有找到对应的记录
            return Response(
                {"success": False, "message": "Image not found in database"},
                status=status.HTTP_404_NOT_FOUND,  # 返回404，表示资源未找到
            )
