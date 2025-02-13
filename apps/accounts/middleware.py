import json
from django.http import HttpResponse
from apps.utils.token_util import parse_token
from django.shortcuts import HttpResponseRedirect
from rest_framework import status


class LoginInterceptorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 获取请求的URL
        url = request.path
        # 开放的URL列表
        open_urls = [
            "/",
            "/admin/",
            "/api/login",
            "/api/send-email-verification-code",
            "/api/register",
            "/api/forgot_password",
            "/api/change_password",
            "/qrcode",
            "/pay/alipay",
            "/search/image/time",
            "/search/image/timezone",
            "/search/image/position",
            "/search/image/tags",
            "/search/image/tag",
            "/search/image/description",
            "/search/image",
            "/qrcode",
            "/qrcode/get",
            "/qrcode/scan",
            "/qrcode/login",
        ]
        # 直接放行的页面
        if url in open_urls or url.startswith("/admin/"):
            return self.get_response(request)
        # 验证用户身份
        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return HttpResponseRedirect("/api/login")
        # 处理 Bearer 类型的 Token
        if token.startswith("Bearer "):
            token = token[7:]  # 去掉 "Bearer " 前缀
        payload = parse_token(token)
        if not payload:
            return HttpResponseRedirect("/api/login")

        return self.get_response(request)
