from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import logging

logger = logging.getLogger("django")

class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        # 进行登录验证，通常是用Django的认证系统
        if username == "test_user" and password == "securepassword":  # 示例验证
            logger.info("User logged in successfully")
            token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # 示例token
            return Response(
                {"status": "success", "token": token}, status=status.HTTP_200_OK
            )
        return Response(
            {"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
        )
