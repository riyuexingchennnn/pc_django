from django.db import models
import uuid


# 图片表
class Image(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )  # 图片唯一标识
    url = models.URLField(max_length=200, default="images/default.png")  # 图片URL
    folder_url = models.URLField(max_length=200, default="我的收藏/")  # 图片文件夹URL
    name = models.CharField(max_length=255)  # 图片名称
    description = models.TextField(blank=True, null=True)  # 图片描述
    category = models.CharField(max_length=100, blank=True, null=True)  # 图片分类
    position = models.CharField(max_length=100, blank=True, null=True)  # 图片位置
    time = models.DateTimeField(blank=True, null=True)  # 上传时间
    user_id = models.CharField(max_length=255)  # 上传用户ID
    image_size = models.FloatField(blank=True, null=True)  # 图片大小，单位为MB

    def __str__(self):
        return self.id  # 返回图片名称作为对象的字符串表示

    class Meta:
        db_table = "image"  # 自定义表名
        verbose_name = "图片"  # 表名的显示名称
        verbose_name_plural = "图片"  # 表名的复数显示名称


# 图片与标签的关系表
class ImageTag(models.Model):
    image_id = models.UUIDField(default=uuid.uuid4, editable=False)  # 图片唯一标识，使用 UUID
    tag_name = models.CharField(max_length=255)  # 标签名称

    def __str__(self):
        return f"Image ID {self.image_id} - {self.tag_name}"  # 返回图片 ID 和标签名的关系

    class Meta:
        db_table = "image_tag"  # 自定义表名
        verbose_name = "图片标签关系"  # 表名的显示名称
        verbose_name_plural = "图片标签关系"  # 表名的复数显示名称
        unique_together = ("image_id", "tag_name")  # 设置联合唯一约束
