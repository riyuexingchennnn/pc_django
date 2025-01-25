import re
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.models import User

import logging

logger = logging.getLogger("django")


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
                {"message": "User does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )
        if user.check_password(password):
                # 示例token
                token = "123"
                return Response(
                    {
                        "token": token
                    },
                    status=status.HTTP_200_OK
                )
        else:
            return Response(
                {"message": "Invalid password"},
                status=status.HTTP_401_UNAUTHORIZED
            )


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        # 验证用户名是否已经存在
        if User.objects.filter(username=username).exists():
            return Response(
                {"message": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # 验证邮箱是否已经存在
        if User.objects.filter(email=email).exists():
            return Response(
                {"message": "Email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # 验证邮箱格式
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            return Response(
                {"message": "Invalid email format"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.create_user(username=username, password=password, email=email)
        # 返回注册成功的信息和用户ID
        return Response(
            {
                "message": "User registered successfully",
                "user_id": user.id
            },
            status=status.HTTP_201_CREATED
        )
