from django.db import models
import uuid

# Create your models here.
class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=200, default="images/default.png")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)
    user_id = models.CharField(max_length=255)

    def __str__(self):
        return self.id  # 返回图片名称作为对象的字符串表示
    
    class Meta:
        db_table = "image"  # 自定义表名
        verbose_name = "图片"  # 自定义表名显示名称
        verbose_name_plural = "图片"  # 自定义表名复数显示名称
