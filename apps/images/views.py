from rest_framework.views import APIView
from rest_framework.response import Response
import logging
import uuid
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError
import base64
from io import BytesIO
import urllib.parse
from .ai_utils.ai import content_filter, image_understanding, image_description
from .models import Image

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
# 因为有众多步骤，所以导致上传图片相对较慢，一张图片大约3.11秒
class UploadImageView(APIView):
    def post(self, request, *args, **kwargs):
        # 获取文件和表单字段
        image_file = request.FILES.get("image")  # 获取图片文件(这个只能一张图片)
        user_id = request.data.get("user_id")  # 获取用户ID
        time = request.data.get("time") or None  # 获取拍摄时间
        category = request.data.get("category") or  "未分类" # 获取分组
        position = request.data.get("position") or None # 获取位置

        # 生成一个唯一的UUID作为文件名
        unique_filename = str(uuid.uuid4())

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

            # result, reason = content_filter(encoded_image)  # 调用AI接口进行内容审核
            # print(result, reason)
            # if result == "不合规":
            #     return Response(
            #         {"success": False, "message": reason}, status=400
            #     )  # 返回400错误，表示请求错误

            # tags = image_understanding(encoded_image)  # 调用AI接口进行图像理解
            # print(tags)
            # description = image_description(encoded_image_raw)  # 调用AI接口进行图像描述
            # print(description)

            # image_instance = Image.objects.create(
            #     name=image_file.name,
            #     description=description,
            #     category="生活",
            #     position=position,
            #     time=time,
            #     id=unique_filename,
            #     user_id=user_id,
            #     url=f"images/{unique_filename}_{image_file.name}"
            # )

            # logger.info(f"Image instance created: {image_instance}")
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return Response(
                {"success": False, "message": "Error reading file"}, status=500
            )
        
        try:
            # 上传COS
            # 设置COS上传对象的键名（使用UUID作为文件名）
            file_extension = image_file.name.split('.')[-1]  # 获取文件扩展名
            object_key = f"images/{unique_filename}.{file_extension}"

            # 上传文件到腾讯云COS
            response = client.upload_file_from_buffer(
                Bucket=bucket_name,
                Key=object_key,
                Body=image_file,
                EnableMD5=False,  # 是否启用MD5验证
            )

            logger.info(f"Upload successful: {response}")

            return Response(
                {
                    "success": True,
                    "message": "Image uploaded successfully",
                },
                status=200,
            )  # 返回状态码200，数据格式为JSON
        
        except (CosClientError, CosServiceError) as e:
            logger.error(f"Error uploading image: {e}")
            return Response(
                {"success": False, "message": "Image upload failed", "error": str(e)},
                status=500,
            )  # 上传失败时，返回500状态码

        
