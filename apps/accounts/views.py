from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.models import User

import logging

logger = logging.getLogger("django")

# 已完成测试
class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        # 进行登录验证，由于没有使用框架的user表，所以需要手动进行验证
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if user.check_password(password):
                #示例token
                token = "123"
                return Response(
                    {
                        "status": "success",
                        "token": token
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": "Invalid password"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(
            {"message": "User does not exist"},
            status=status.HTTP_404_NOT_FOUND
        )

#已完成测试
class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        if User.objects.filter(username=username).exists():
            return Response(
                {"message": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if User.objects.filter(email=email).exists():
            return Response(
                {"message": "Email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.create_user(username=username, password=password, email=email)
        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED
        )
