import re
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.models import User
from apps.notifications.views import send_mail
from django.contrib.auth.hashers import make_password
import logging, random, string

logger = logging.getLogger("django")


# 已完成测试
class LoginView(APIView):
    def post(self, request):
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        username_or_email = request.data.get("username_or_email")
        password = request.data.get("password")
        # 进行登录验证，由于没有使用框架的user表，所以需要手动进行验证
        # 这里支持邮箱和用户名登录
        user = None
        if re.match(email_regex, username_or_email):
            if User.objects.filter(email=username_or_email).exists():
                user = User.objects.get(email=username_or_email)
        elif User.objects.filter(username=username_or_email).exists():
            user = User.objects.get(username=username_or_email)
        if user is None:
            return Response(
                {"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        if user.check_password(password):
            # 示例token
            token = "123"
            return Response({"token": token}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED
            )


# 已完成测试
class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        # 验证用户名是否已经存在
        if User.objects.filter(username=username).exists():
            return Response(
                {"message": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 验证邮箱是否已经存在
        if User.objects.filter(email=email).exists():
            return Response(
                {"message": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST
            )
        # 验证邮箱格式
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            return Response(
                {"message": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.create_user(
            username=username, password=password, email=email
        )
        # 返回注册成功的信息和用户ID
        return Response(
            {"message": "User registered successfully", "user_id": user.id},
            status=status.HTTP_201_CREATED,
        )


# 已完成测试
class ChangePasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        # 验证邮箱格式
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            return Response(
                {"message": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST
            )
        # 验证邮箱是否存在
        if not User.objects.filter(email=email).exists():
            return Response(
                {"message": "Email does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        user = User.objects.get(email=email)
        # 修改密码分为两个阶段，验证码请求、验证码验证
        is_verifying = request.data.get("is_verifying")
        # 验证码请求
        if not is_verifying:
            # 生成验证码
            all_characters = string.ascii_letters + string.digits
            verification_code = "".join(random.choice(all_characters) for _ in range(6))
            # 保存验证码到数据库
            user.verification_code = verification_code
            # 这个函数是必须要的
            user.save()
            # 发送验证码到邮箱
            send_mail(
                recipient_list=[email],
                subject="修改密码请求",
                body="尊敬的影云用户("
                + email
                + ")您好，您关于修改密码的验证码如下: "
                + verification_code,
            )
            return Response(
                {"message": "Verification code sent"}, status=status.HTTP_200_OK
            )
        # 验证码验证
        else:
            # 先须要获取验证码 ，这里主要是为了逻辑完备
            # md单词打错bug找半天
            if user.verification_code is None:
                return Response(
                    {"message": "No verification code found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            verification_code = request.data.get("verification_code")
            new_password = request.data.get("new_password")
            if user.verification_code == verification_code:
                # 能否直接用set_password函数需要测试
                user.password = make_password(new_password)
                user.save()
                return Response(
                    {"message": "Password changed successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Invalid verification code"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


# 未测试
class ChangeInfoView(APIView):
    def post(self, request):
        # todo : 所有操作之前都需要验证用户身份
        # 原用户名是必传参数
        username = request.data.get("username")
        user = User.objects.get(username=username)
        # 修改邮箱
        if request.data.get("email"):
            email = request.data.get("email")
            # 验证邮箱格式
            email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_regex, email):
                return Response(
                    {"message": "Invalid email format"},
                )
            user.email = email
            user.save()
        # 这里注意修改密码需要同时提供原密码
        if request.data.get("password"):
            password = request.data.get("password")
            if user.check_password(password):
                if request.data.get("new_password"):
                    new_password = request.data.get("new_password")
                    user.password = make_password(new_password)
                    user.save()
            else:
                return Response(
                    {"message": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST
                )
        # 修改用户名
        if request.data.get("new_username"):
            new_username = request.data.get("new_username")
            user.username = new_username
            user.save()
        # 返回修改成功的信息
        return Response(
            {"message": "Info changed successfully"}, status=status.HTTP_200_OK
        )


# 未测试
class ChangeAvatarView(APIView):
    def post(self, request):
        # todo : 所有操作之前都需要验证用户身份
        username = request.data.get("username")
        user = User.objects.get(username=username)
        user.avatar = request.data.get("avatar")
        user.save()
        return Response(
            {"message": "Avatar changed successfully"}, status=status.HTTP_200_OK
        )
