from django.db import models
from django.db.models import BooleanField, CharField, FloatField, ForeignKey
from django.db.models import DateTimeField
from apps.accounts.models import User


# Create your models here.


class ConsumptionHistory(models.Model):
    """
    消费（充值）记录
    """

    trade_no = models.UUIDField(primary_key=True, help_text="订单号")
    user_id = models.ForeignKey(
        to=User, to_field="id", on_delete=models.CASCADE, help_text="用户id"
    )
    trade_time = DateTimeField(auto_now=True, help_text="交易时间")
    trade_spent = FloatField(help_text="消费金额")
    is_success = BooleanField(default=False, help_text="是否成功")
    trade_description = CharField(max_length=4, null=True, help_text="套餐类型")

    class Meta:
        db_table = "consumption_history"


class ContinueTime(models.Model):
    """
    会员持续时间
    """

    user = ForeignKey(
        to=User, to_field="id", on_delete=models.CASCADE, help_text="用户id"
    )
    type = CharField(max_length=4, help_text="会员类型")
    deadline = DateTimeField(help_text="会员截止时间")

    class Meta:
        db_table = "continue_time"
