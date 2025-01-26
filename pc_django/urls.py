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
from apps.images.views import (
    UploadImageView,
    DeleteImageView,
    UpdateImageView,
    DownloadImageView,
)
from apps.pay.views import AlipayView
from apps.search.views import (
    SelectImagesByTime,
    SelectImagesByPosition,
    SelectImagesByTags,
)
urlpatterns = [
    path("admin/", admin.site.urls),  # Django 自带的后台管理系统
    # ------------------------------ accounts ------------------------------
    # 登录页面
    path("user/login", LoginView.as_view(), name="login"),
    # 注册
    path("user/register", RegisterView.as_view(), name="register"),
    # ----------------------------------------------------------------------
    # ------------------------------ images --------------------------------
    # 图片上传
    path("image/upload", UploadImageView.as_view(), name="upload_image"),
    # 图片删除
    path("image/delete", DeleteImageView.as_view(), name="delete_image"),
    # 图片更新
    path("image/update", UpdateImageView.as_view(), name="update_image"),
    # 图片下载
    path("image/download", DownloadImageView.as_view(), name="download_image"),
    # ----------------------------------------------------------------------
    # ------------------------------ pay -------------------------------------
    # 支付
    path("pay/alipay", AlipayView.as_view(), name="alipay"),
    path("pay/alipay", AlipayView.as_view(), name="alipay_success"),
    # path("pay/alipay/notify", alipay_notify)
    # -------------------------------------------------------------------------
    # ------------------------------ search -------------------------------------
    # 搜索图片
    path("search/image/time", SelectImagesByTime.as_view(), name="search_images_time"),
    path("search/image/position", SelectImagesByPosition.as_view(), name="search_images_position"),
    path("search/image/tags", SelectImagesByTags.as_view(), name="search_images_tags"),
]
