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
from apps.accounts.admin import custom_admin_site

# 导入自定义的视图函数
from apps.accounts.views import (
    LoginView,
    RegisterView,
    VerifyTokenView,
    SendCodeView,
    UserInfoView,
    LoginOutView,
    RefreshTokenView,
    ChangePasswordView,
    ChangeInfoView,
    DeleteUserView,
    ForgetPasswordView,
)
from apps.images.views import (
    UploadImageView,
    DeleteImageView,
    UpdateImageView,
    DownloadImageView,
)
from apps.pay.views import AlipayView, GetUserMembership
from apps.search.views import (
    SelectImagesByTime,
    SelectImagesByTimeZone,
    SelectImagesByPosition,
    SelectImagesByTags,
    SelectImagesByDescription,
    SelectImagesByTPT,
    GetTags,
    GetProvinces,
    GetCity,
    GetDistrict,
)
from apps.qr_code.views import (
    QRcodeView,
    QRcodeStateView,
    PhoneScanned,
    QRcodeLoginView,
)


urlpatterns = [
    #path("admin/", admin.site.urls),  # Django 自带的后台管理系统
    path("admin/", custom_admin_site.urls),  # Django 自带的后台管理系统
    # ------------------------------ accounts ------------------------------
    # 登录页面
    path("api/login", LoginView.as_view(), name="login"),
    # 注册
    path("api/register", RegisterView.as_view(), name="register"),
    # Token 验证
    path("api/validate-token", VerifyTokenView.as_view(), name="token"),
    # 发送注册验证码
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
    # 忘记密码
    path("api/change_password", ChangePasswordView.as_view(), name="change_password"),
    # 发送忘记密码的验证码
    path("api/forget_password", ForgetPasswordView.as_view(), name="change_info"),
    # 基础信息修改
    path("api/change_info", ChangeInfoView.as_view(), name="change_info"),
    # 用户注销
    path("api/delete_user", DeleteUserView.as_view(), name="delete_user"),
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
    path(
        "pay/getmembership", GetUserMembership.as_view(), name="get_user's_membership"
    ),
    # path("pay/alipay", AlipayView.as_view(), name="alipay_success"),
    # path("pay/alipay/notify", alipay_notify)
    # -------------------------------------------------------------------------
    # ------------------------------ search -------------------------------------
    # 搜索图片
    path("search/image/time", SelectImagesByTime.as_view(), name="search_images_time"),
    path(
        "search/image/timezone",
        SelectImagesByTimeZone.as_view(),
        name="search_image_timezone",
    ),
    path(
        "search/image/position",
        SelectImagesByPosition.as_view(),
        name="search_images_position",
    ),
    path("search/image/tags", SelectImagesByTags.as_view(), name="search_images_tags"),
    path("search/image/tag", GetTags.as_view(), name="get_tags"),
    path(
        "search/image/description",
        SelectImagesByDescription.as_view(),
        name="search_images_description",
    ),
    path("search/image", SelectImagesByTPT.as_view(), name="search_image"),
    path("search/position/province", GetProvinces.as_view(), name="get_province"),
    path("search/position/city", GetCity.as_view(), name="get_city"),
    path("search/position/district", GetDistrict.as_view(), name="get_district"),
    # -----------------------------------------------------------------------------
    # ------------------------------ qr_code -------------------------------------
    path("qrcode", QRcodeView.as_view(), name="get_QRcode"),
    path("qrcode/get", QRcodeStateView.as_view(), name="get_QRcode_state"),
    path("qrcode/scan", PhoneScanned.as_view(), name="phone_scan"),
    path("qrcode/login", QRcodeLoginView.as_view(), name="qrcode_login"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
