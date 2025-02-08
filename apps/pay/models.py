from django.db import models
from django.db.models import BooleanField, IntegerField, CharField
from django.db.models import DateTimeField
from apps.accounts.models import User


# Create your models here.
class BaseModel(models.Model):
    """
    基类
    """

    class Meta:
        abstract = True
        ordering = ["-created_time"]

    def __str__(self):
        raise NotImplementedError


class consumptionHistory(BaseModel):
    """
    消费（充值）记录
    """

    trade_no = models.UUIDField(primary_key=True, help_text="订单号")
    user_id = models.ForeignKey(
        to=User, to_field="id", on_delete=models.CASCADE, help_text="用户id"
    )
    trade_time = DateTimeField(auto_now=True, help_text="交易时间")
    trade_spent = IntegerField(help_text="消费金额")
    is_success = BooleanField(default=False, help_text="是否成功")
    trade_description = CharField(max_length=4, null=True, help_text="套餐类型")

    class Meta:
        db_table = "consumptionHistory"
