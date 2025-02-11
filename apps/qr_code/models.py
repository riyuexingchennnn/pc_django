import uuid
from django.db import models

# Create your models here.


class QRcodeId(models.Model):
    """
    二维码表
    """

    qrcode_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.CharField(
        max_length=10, default="unused", help_text="二维码使用情况"
    )

    class Meta:
        db_table = "qrcode_id"


class TemporaryToken(models.Model):
    temporary_token = models.UUIDField(primary_key=True, help_text="临时token")
    qrcode = models.ForeignKey(
        to=QRcodeId,
        to_field="qrcode_id",
        on_delete=models.CASCADE,
        help_text="二维码id",
    )
    user = models.IntegerField(help_text="用户id", null=True)

    class Meta:
        db_table = "temporary_token"
