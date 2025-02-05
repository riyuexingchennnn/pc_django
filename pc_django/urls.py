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
from django.conf import settings
from django.conf.urls.static import static

# 导入自定义的视图函数
from apps.accounts.views import (
    LoginView,
    RegisterView,
    VerifyTokenView,
    SendCodeView,
    UserInfoView,
    LoginOutView,
    RefreshTokenView,
    ChangeAvatarView,
    ChangePasswordView,
    ChangeInfoView,
)
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
    SelectImagesByDescription,
)

urlpatterns = [
    path("admin/", admin.site.urls),  # Django 自带的后台管理系统
    # ------------------------------ accounts ------------------------------
    # 登录页面
    path("api/login", LoginView.as_view(), name="login"),
    # 注册
    path("api/register", RegisterView.as_view(), name="register"),
    # Token 验证
    path("api/validate-token", VerifyTokenView.as_view(), name="token"),
    # 发送验证码
    path(
        "api/send-email-verification-code",
        SendCodeView.as_view(),
        name="send_verification_code",
    ),
    # 获取用户信息
    path("api/user-info", UserInfoView.as_view(), name="user_info"),
    # 登出
    path("api/logout", LoginOutView.as_view(), name="logout"),
    # 通过refresh_token刷新access_token
    path("api/refresh-token", RefreshTokenView.as_view(), name="refresh_token"),
    # 以下URL未测试
    # 基础信息修改
    path("user/change_info", ChangeInfoView.as_view(), name="change_info"),
    # 头像修改
    path("user/change_avatar", ChangeAvatarView.as_view(), name="change_avatar"),
    # 修改密码
    path("user/change_password", ChangePasswordView.as_view(), name="change_password"),
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
    path(
        "search/image/position",
        SelectImagesByPosition.as_view(),
        name="search_images_position",
    ),
    path("search/image/tags", SelectImagesByTags.as_view(), name="search_images_tags"),
    path(
        "search/image/description",
        SelectImagesByDescription.as_view(),
        name="search_images_description",
    ),
    # -----------------------------------------------------------------------------
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
