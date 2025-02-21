from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError

# 腾讯云 COS 相关配置
secret_id = ""
secret_key = ""
region = "ap-guangzhou"  # 你COS桶所在的区域（例如：'ap-guangzhou'）
bucket_name = "***REMOVED***"  # 替换成你的COS存储桶名称

# 初始化CosConfig和CosS3Client
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
client = CosS3Client(config)


# 上传文件到腾讯云COS
def upload_image_cos(image_id, image_file):
    # 设置COS上传对象的键名（使用UUID作为文件名）
    file_extension = image_file.name.split(".")[-1]  # 获取文件扩展名
    # print(file_extension)
    object_key = f"images/{image_id}.{file_extension}"
    response = client.upload_file_from_buffer(
        Bucket=bucket_name,
        Key=object_key,
        Body=image_file,
        EnableMD5=False,  # 是否启用MD5验证
    )
    return response, object_key


# 删除文件在COS上的存储
def delete_image_cos(image_url):
    object_key = image_url
    response = client.delete_object(
        Bucket=bucket_name,
        Key=object_key,
    )
    return response


# 生成COS图片签名URL
def generate_image_url_cos(image_url, expiration=900):
    object_key = image_url  # 获取COS中图片的路径
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
    return presigned_url
