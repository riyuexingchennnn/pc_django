import re, logging, random, string, jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import os
from apps.accounts.models import User, VerificationCode
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.cache import cache

from apps.utils.email_util import send_mail
from apps.utils.token_util import parse_token

logger = logging.getLogger("django")

def create_code_and_send(email):
    # 生成验证码并保存
    verificationCode = VerificationCode()
    code = verificationCode.create_code(email)
    # 发送验证码到邮箱
    send_mail(
        recipient_list=[email],
        subject="影云验证码",
        body=f"""
        <html>
        <body>
            <p>尊敬的影云用户 {email}，您好！</p>
            
            <p>您的验证码如下：</p>
            
            <div style="font-size: 24px; font-weight: bold; color: #4CAF50;">
                {code}
            </div>
            
            <p>为确保账户安全，验证码将在 5 分钟后过期，请及时使用。</p>
            
            <p>如果您没有请求此验证码，请忽略此邮件。</p>
            
            <p>祝您使用愉快！</p>
            
            <p>影云团队</p>
        </body>
        </html>
        """,
    )
# 检查会话是否过期
class VerifyTokenView(APIView):
    def post(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        if token is None:
            return Response(
                {"status": "error", "message": "未提供token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # 解析token
        payload = parse_token(token)
        # token过期或者无效
        if payload is None:
            return Response(
                {"status": "error", "message": "token 无效或已过期"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(
            {"status": "success", "message": "token 有效"},
            status=status.HTTP_200_OK,
        )


# 刷新access_token
class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.META.get("HTTP_AUTHORIZATION")
        if refresh_token is None:
            return Response(
                {"status": "error", "message": " refresh_token 不能为空"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payload = parse_token(refresh_token)
        if payload is None:
            return Response(
                {"status": "error", "message": " refresh_token 无效"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        user_id = payload["user_id"]
        # access_token生成
        expiration_time = timezone.now() + timezone.timedelta(minutes=15)
        payload = {
            "user_id": user_id,
            "exp": expiration_time,
        }
        access_token = jwt.encode(payload, "secret_code", algorithm="HS256")
        return Response(
            {"access_token": access_token},
        )


# 登录
class LoginView(APIView):
    def post(self, request):
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        email = request.data.get("email")
        password = request.data.get("password")
        # 进行登录验证，由于没有使用框架的user表，所以需要手动进行验证
        user = None
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
        if user is None:
            return Response({"status": "error", "message": "用户不存在"}, status=status.HTTP_400_BAD_REQUEST)
        if user.check_password(password):
            # access_token生成
            expiration_time = timezone.now() + timezone.timedelta(minutes=15)
            payload = {
                "user_id": user.id,
                "exp": expiration_time,
            }
            access_token = jwt.encode(payload, "secret_code", algorithm="HS256")
            # refresh_token生成
            expiration_time = timezone.now() + timezone.timedelta(days=7)
            payload = {
                "user_id": user.id,
                "exp": expiration_time,
            }
            refresh_token = jwt.encode(payload, "secret_code", algorithm="HS256")
            return Response(
                {
                    "status": "success",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "base_login_name": user.username,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": "error", "message": "用户名或密码错误"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


# 使用验证码注册
class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        verificationCode = request.data.get("verificationCode")
        # 验证用户名是否已经存在
        if User.objects.filter(username=username).exists():
            return Response(
                {"message": "用户名已存在"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 验证邮箱格式
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            return Response(
                {"message": "邮箱格式不正确"}, status=status.HTTP_400_BAD_REQUEST
            )
        # 验证邮箱是否已经存在
        if User.objects.filter(email=email).exists():
            return Response(
                {"message": "邮箱已被注册"}, status=status.HTTP_400_BAD_REQUEST
            )
        code = VerificationCode.objects.get(email=email)
        # 验证码不存在
        if code is None:
            return Response(
                {"message": "验证码不存在"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 验证码不匹配
        if code.code != verificationCode:
            return Response(
                {"message": "验证码不匹配"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 验证码过期
        if code.is_expired():
            return Response(
                {"message": "验证码已过期"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.create_user(
            username=username, password=password, email=email
        )
        # 返回注册成功的信息和用户ID
        return Response(
            {"message": "用户注册成功", "user_id": user.id},
            status=status.HTTP_201_CREATED,
        )


# 发送注册验证码
class SendCodeView(APIView):
    def post(self, request):
        email = request.data.get("email")
        # 验证邮箱格式
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            return Response(
                {"status": "error", "message": "邮箱格式不正确"}, status=status.HTTP_400_BAD_REQUEST
            )
        # 验证邮箱是否存在
        if User.objects.filter(email=email).exists():
            return Response(
                {"status": "error", "message": "邮箱已被注册"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        create_code_and_send(email)
        # 返回发送成功的信息和验证码
        return Response(
            {"status": "success", "message": "验证码发送成功"},
            status=status.HTTP_200_OK,
        )


# 获取用户信息,可以通过返回的URL直接访问头像
class UserInfoView(APIView):
    def post(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        payload = parse_token(token)
        user_id = payload.get("user_id")
        user = User.objects.get(id=user_id)
        return Response(
            {
                "status": "success",
                "username": user.username,
                "email": user.email,
                "avatar": request.build_absolute_uri(user.avatar.url),
                "membership": user.membership,
                "space": user.used_space,
                "user_id": user.id,
            },
            status=status.HTTP_200_OK,
        )
# 登出
class LoginOutView(APIView):
    def post(self, request):
        refresh_token = request.META.get("HTTP_AUTHORIZATION")
        if not refresh_token:
            return Response(
                {"message": "token未提供"}, status=status.HTTP_400_BAD_REQUEST
            )
        cache.set(refresh_token, True, 604800) # 拉黑7天
        return Response({"message": "成功退出登录"}, status=status.HTTP_200_OK)


# 忘记密码, 已测试
class ChangePasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        verification_code = request.data.get("verification_code")
        new_password = request.data.get("new_password")
        # 验证邮箱格式
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            return Response(
                {"message": "邮箱格式不正确"}, status=status.HTTP_400_BAD_REQUEST
            )
        # 验证邮箱是否存在
        if not User.objects.filter(email=email).exists():
            return Response({"message": "邮箱不存在"}, status=status.HTTP_404_NOT_FOUND)
        user = User.objects.get(email=email)
        code = VerificationCode.objects.get(email=email)
        # 验证码不存在
        if code is None:
            return Response(
                {"message": "验证码不存在"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 验证码不匹配
        if code.code != verification_code:
            return Response(
                {"message": "验证码不匹配"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 验证码过期
        if code.is_expired():
            return Response(
                {"message": "验证码已过期"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.password = make_password(new_password)
        user.save()
        return Response(
            {"message": "密码修改成功"},
            status=status.HTTP_200_OK,
        )


# 发送忘记密码的验证码
class ForgetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        # 验证邮箱格式
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            return Response(
                {"status": "error", "message": "邮箱格式不正确"}, status=status.HTTP_400_BAD_REQUEST
            )
        # 验证邮箱是否存在
        if not User.objects.filter(email=email).exists():
            return Response(
                {"status": "error", "message": "邮箱未被注册"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        #60秒不可重复发送
        code = VerificationCode.objects.get(email=email)
        if code is not None and code.is_sleep:
            return Response(
                {"status": "error", "message": "请60秒后再试"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        create_code_and_send(email)
        # 返回发送成功的信息和验证码
        return Response(
            {"status": "success", "message": "验证码发送成功"},
            status=status.HTTP_200_OK,
        )


# 信息修改
class ChangeInfoView(APIView):
    def post(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        payload = parse_token(token)
        user_id = payload.get("user_id")
        user = User.objects.get(id=user_id)
        # 修改邮箱
        if request.data.get("new_email"):
            new_email = request.data.get("new_email")
            # 验证邮箱格式
            email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_regex, new_email):
                return Response(
                    {"message": "邮箱格式不正确"},
                )
            user.email = new_email
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
                    {"message": "密码不正确"}, status=status.HTTP_400_BAD_REQUEST
                )
            
        # 修改用户名
        if request.data.get("username"):
            new_username = request.data.get("username")
            user.username = new_username
            user.save()

        # 修改用户头像
        if request.FILES.get("avatar"):
            print("获取头像 " , request.FILES.get("avatar"))
            new_avatar = request.FILES.get("avatar")

            new_avatar.seek(0)  # 移动文件指针到开头
            # file_extension = new_avatar.name.split(".")[-1]  # 获取文件扩展名

            # avatar_filename = f"{user_id}.{file_extension}"  # 使用用户ID命名头像文件，可以根据需求调整文件扩展名
            avatar_filename = f"{user_id}.jpg"  # 使用jpg命名，图像体积小

            # 保存到 media/avatar 目录下
            avatar_path = os.path.join(settings.MEDIA_ROOT, "avatar", avatar_filename)

            # 确保目录存在
            if not os.path.exists(os.path.dirname(avatar_path)):
                os.makedirs(os.path.dirname(avatar_path))

            # 保存文件
            with default_storage.open(avatar_path, "wb+") as destination:
                for chunk in new_avatar.chunks():
                    destination.write(chunk)

            # 更新用户的头像路径
            user.avatar = os.path.join("avatar", avatar_filename)  # 存储相对路径
            user.save()
        # 返回修改成功的信息
        return Response({"message": "修改信息成功"}, status=status.HTTP_200_OK)


# 用户删除
class DeleteUserView(APIView):
    def post(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        payload = parse_token(token)
        user_id = payload.get("user_id")
        user = User.objects.get(id=user_id)
        user.delete()
        return Response({"message": "用户注销成功"}, status=status.HTTP_200_OK)
