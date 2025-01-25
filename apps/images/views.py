from rest_framework.views import APIView
from rest_framework.response import Response
import logging
import uuid
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError
import base64
import urllib.parse
from django.core.exceptions import ObjectDoesNotExist

from .ai_utils.ai import content_filter, image_understanding, image_description
from .models import Image, ImageTag
from apps.accounts.models import User

# 腾讯云 COS 相关配置
secret_id = "***REMOVED***"
secret_key = "***REMOVED***"
region = "ap-guangzhou"  # 你COS桶所在的区域（例如：'ap-guangzhou'）
bucket_name = "***REMOVED***"  # 替换成你的COS存储桶名称

# 初始化CosConfig和CosS3Client
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
client = CosS3Client(config)

# 设置日志
logger = logging.getLogger("django")


# 上传图片视图
# 因为有众多步骤，所以导致上传图片相对较慢，一张图片大约8.81秒
# 如果是普通会员，没有图像描述功能，上传时间大约为4-7秒
class UploadImageView(APIView):
    def post(self, request, *args, **kwargs):
        # 获取文件和表单字段
        image_file = request.FILES.get("image")  # 获取图片文件(这个只能一张图片)
        user_id = request.data.get("user_id")  # 获取用户ID
        time = request.data.get("time") or None  # 获取拍摄时间
        category = request.data.get("category") or "未分类"  # 获取分组
        position = request.data.get("position") or None  # 获取位置

        # 生成一个唯一的UUID作为文件名
        image_id = str(uuid.uuid4())

        logger.debug(
            f"Metadata - user_id: {user_id}, time: {time}, category: {category}, position: {position}, name: {image_file.name}"
        )

        # 验证必填字段，图片文件
        if not image_file or not user_id:
            return Response(
                {"success": False, "message": "Image file and user_id is required"},
                status=400,
            )  # 返回400错误，表示请求错误

        # 检查文件大小，确保不会超过限制
        if image_file.size > 10 * 1024 * 1024:  # 设置最大文件大小为10MB
            return Response(
                {"success": False, "message": "File is too large. Max size is 10MB."},
                status=400,
            )

        # 确保文件可以读取
        try:
            ############################
            # 注意image_file.read()方法
            # 要用文件指针归零
            ############################
            image_data = image_file.read()  # 读取图片数据
            image_file.seek(0)  # 将指针重置到文件的开头!!!

            # 将图片数据转换为 Base64 编码
            encoded_image_raw = base64.b64encode(image_data).decode("utf-8")
            encoded_image = urllib.parse.quote_plus(
                encoded_image_raw
            )  # 这个函数用于将字符串进行 URL 编码

            result, reason = content_filter(encoded_image)  # 调用AI接口进行内容审核
            # print(result, reason)
            if result == "不合规":
                return Response(
                    {"success": False, "message": reason}, status=400
                )  # 返回400错误，表示请求错误

            tags = image_understanding(encoded_image)  # 调用AI接口进行图像理解
            # print(tags)

            description = "此图片没有描述"
            # 如果是普通会员
            if not User.objects.get(id=user_id).membership == "free":
                description = image_description(
                    encoded_image_raw
                )  # 调用AI接口进行图像描述
            # print(description)

            category = "生活"  # 固定分组为“生活”

        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return Response(
                {"success": False, "message": "Error reading file"}, status=500
            )

        try:
            # 上传COS
            # 设置COS上传对象的键名（使用UUID作为文件名）
            file_extension = image_file.name.split(".")[-1]  # 获取文件扩展名
            object_key = f"images/{image_id}.{file_extension}"

            # 上传文件到腾讯云COS
            response = client.upload_file_from_buffer(
                Bucket=bucket_name,
                Key=object_key,
                Body=image_file,
                EnableMD5=False,  # 是否启用MD5验证
            )
            logger.info(f"COS Upload successful: {response}")

            image_instance = Image.objects.create(
                name=image_file.name,
                description=description,
                category=category,
                position=position,
                time=time,
                id=image_id,
                user_id=user_id,
                url=object_key,
            )

            logger.info(f"Image instance created: {image_instance}")

            # 构建图像标签关系表
            # 如果标签不存在，则创建标签
            for tag_name in tags:
                ImageTag.objects.get_or_create(tag_name=tag_name, image=image_instance)

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
                    "tags": tags,
                },
                status=200,
            )  # 返回状态码200，数据格式为JSON

        except (CosClientError, CosServiceError) as e:
            logger.error(f"Error uploading image: {e}")
            return Response(
                {"success": False, "message": "Image upload failed", "error": str(e)},
                status=500,
            )  # 上传失败时，返回500状态码


# 删除图片视图
class DeleteImageView(APIView):
    def post(self, request, *args, **kwargs):
        # 获取图片ID
        image_id = request.data.get("image_id")
        user_id = request.data.get("user_id")

        # 验证必填字段
        if not image_id or not user_id:
            return Response(
                {"success": False, "message": "Image id and user_id is required"},
                status=400,  # 返回400错误，表示请求错误
            )

        try:
            # 查找数据库中的图片记录
            image_record = Image.objects.get(id=image_id)

            # 删除图像标签关系表中的记录
            ImageTag.objects.filter(image=image_record).delete()

            # 获取COS中图片的路径
            object_key = image_record.url

            # 删除COS中的对象
            response = client.delete_object(
                Bucket=bucket_name,
                Key=object_key,
            )
            logger.info(f"COS Delete successful: {response}")

            # 删除数据库中的记录
            image_record.delete()

            return Response(
                {"success": True, "message": "Image deleted successfully"},
                status=200,  # 返回200，表示成功
            )
        except ObjectDoesNotExist:
            # 如果数据库中没有找到对应的记录
            return Response(
                {"success": False, "message": "Image not found in database"},
                status=404,  # 返回404，表示资源未找到
            )


# 修改图片视图
class UpdateImageView(APIView):
    def post(self, request, *args, **kwargs):
        # 获取图片ID
        image_id = request.data.get("image_id")
        user_id = request.data.get("user_id")
        name = request.data.get("name")
        description = request.data.get("description")
        category = request.data.get("category")
        position = request.data.get("position")
        time = request.data.get("time")
        tags = request.data.get("tags")

        if not image_id:
            return Response(
                {"success": False, "message": "Image id is required"},
                status=400,  # 返回400错误，表示请求错误
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
            image_record.save()

            ImageTag.objects.filter(image=image_record).delete()
            for tag_name in tags:
                ImageTag.objects.create(tag_name=tag_name, image=image_record)

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
                },
                status=200,  # 返回200，表示成功
            )
        except ObjectDoesNotExist:
            # 如果数据库中没有找到对应的记录
            return Response(
                {"success": False, "message": "Image not found in database"},
                status=404,  # 返回404，表示资源未找到
            )


# 下载图片视图
class DownloadImageView(APIView):
    def post(self, request, *args, **kwargs):
        # 获取用户ID
        user_id = request.data.get("user_id")
        ####################################
        # 也许还要加入本地已经有的云端图片id列表
        ####################################

        # 验证必填字段
        if not user_id:
            return Response(
                {"success": False, "message": "User id is required"},
                status=400,  # 返回400错误，表示请求错误
            )

        try:
            # 查找数据库中的图片记录
            image_records = Image.objects.filter(user_id=user_id)

            images = []

            # 下载图片
            for image_record in image_records:
                try:
                    # 设置URL过期时间（单位：秒）
                    expiration = 900  # 15分钟过期

                    object_key = image_record.url  # 获取COS中图片的路径
                    # 生成签名URL
                    presigned_url = client.get_presigned_url(
                        Method="GET",  # 指定HTTP方法为GET
                        Bucket=bucket_name,
                        Key=object_key,
                        Expired=expiration,
                        # Params={
                        #     'response-content-disposition': 'inline',  # 确保直接预览
                        # }
                    )

                    logger.debug(f"签名URL: {presigned_url}")

                    tags = ImageTag.objects.filter(image=image_record).values_list(
                        "tag_name", flat=True
                    )

                    image_info = {
                        "name": image_record.name,
                        "description": image_record.description,
                        "category": image_record.category,
                        "position": image_record.position,
                        "time": image_record.time,
                        "id": image_record.id,
                        "presigned_url": presigned_url,
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
                        status=505,  # 返回505错误，表示服务器内部错误
                    )

            return Response(
                {"success": True, "message": images},
                status=200,  # 返回200，表示成功
            )
        except ObjectDoesNotExist:
            # 如果数据库中没有找到对应的记录
            return Response(
                {"success": False, "message": "Image not found in database"},
                status=404,  # 返回404，表示资源未找到
            )
