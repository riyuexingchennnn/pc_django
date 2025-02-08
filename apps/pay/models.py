from django.db import models
from django.db.models.fields import DateTimeField, IntegerField, CharField


# Create your models here.
# class BaseModel(models.Model):
#     """
#     基类
#     """
#
#     class Meta:
#         abstract = True
#         ordering = ["-created_time"]
#
#     created_time = models.DateTimeField(auto_now_add=True, help_text="创建时间")
#     last_modified = models.DateTimeField(auto_now=True, help_text="修改时间")
#
#     def __str__(self):
#         raise NotImplementedError


# class consumptionHistory(BaseModel):
#     """
#     消费（充值）记录
#     """
#
#     trade_id = models.UUIDField()
#     user_id = models.For
#     trade_time = DateTimeField()
#     trade_spent = IntegerField()
#     trade_description = CharField(max_length=4)
#     trade_pattern = CharField(max_length=10)
