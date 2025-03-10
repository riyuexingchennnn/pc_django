from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.utils import timezone
import random, string


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        """
        创建并返回一个标准的用户
        """
        if not email:
            raise ValueError("邮箱是必填项")
        email = self.normalize_email(email)  # 归一化邮箱
        user = self.model(username=username, email=email, **extra_fields)
        # 加密密码
        user.password = make_password(password)
        user.save(using=self._db)  # 保存用户
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        创建并返回超级用户
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)


class User(models.Model):

    used_space = models.FloatField(default=0.0, verbose_name="消耗空间")  # 单位MB
    username = models.CharField(max_length=150, unique=True, verbose_name="用户名")
    email = models.EmailField(unique=True, verbose_name="邮箱")
    password = models.CharField(max_length=255, verbose_name="密码", blank=True)
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="头像",
        default="avatar/default.png",
    )
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="注册时间")
    last_login = models.DateTimeField(auto_now=True, verbose_name="最后登录时间")
    is_active = models.BooleanField(default=True, verbose_name="是否在线")

    MEMBERSHIP_CHOICES = [
        ("free", "免费会员"),
        ("silver", "银牌会员"),
        ("gold", "金牌会员"),
    ]
    membership = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_CHOICES,
        default="free",
        verbose_name="会员权限",
    )

    objects = CustomUserManager()  # 使用自定义的用户管理器

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]  # 必填字段

    class Meta:
        db_table = "user"
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return self.username

    def check_password(self, password):
        return check_password(password, self.password)


# 验证码
class VerificationCode(models.Model):
    email = models.EmailField(unique=True, verbose_name="邮箱")
    code = models.CharField(max_length=6, verbose_name="验证码")
    time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = "verification_code"
        verbose_name = "验证码"
        verbose_name_plural = "验证码"

    def __str__(self):
        return self.email

    objects = models.Manager()

    def is_expired(self):
        # 判断验证码是否过期
        return timezone.now() > self.time + timezone.timedelta(minutes=5)
    def is_sleep(self):
        # 判断验证码是否过期
        return timezone.now() < self.time + timezone.timedelta(minutes=1)

    def create_code(self, email):
        if VerificationCode.objects.filter(email=email).exists():
            VerificationCode.objects.filter(email=email).delete()
        verificationCode = VerificationCode(
            email=email, code="".join(random.sample(string.digits, 6))
        )
        verificationCode.save()
        return verificationCode.code
