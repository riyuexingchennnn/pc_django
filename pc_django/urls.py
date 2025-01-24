"""
URL configuration for pc_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

# 导入自定义的视图函数
from apps.accounts.views import LoginView, RegisterView
from apps.images.views import ImageUploadView

# 暂时用不了
# from rest_framework import permissions
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi

# schema_view = get_schema_view(
#    openapi.Info(
#       title="API Documentation",
#       default_version='v1',
#       description="Test API",
#       terms_of_service="https://www.google.com/policies/terms/",
#       contact=openapi.Contact(email="contact@myapi.com"),
#       license=openapi.License(name="BSD License"),
#    ),
#    public=True,
#    permission_classes=(permissions.AllowAny,),
# )

urlpatterns = [
    path("admin/", admin.site.urls),  # Django 自带的后台管理系统
    # 登录页面
    path("api/v1/user/login", LoginView.as_view(), name="login"),
    # 注册
    path("api/v1/user/register", RegisterView.as_view(), name="register"),
    # 图片上传
    path("upload-image/", ImageUploadView.as_view(), name="upload_image"),
]
