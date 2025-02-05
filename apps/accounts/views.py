import re, logging, random, string, jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.models import User, VerificationCode
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.core.cache import cache

from apps.utils.email_util import send_mail
from apps.utils.token_util import parse_token

logger = logging.getLogger("django")


# 检查会话是否过期,待测试
class VerifyTokenView(APIView):
    def post(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        if token is None:
            return Response(
                {"status": "error", "message": "Token not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # 解析token
        payload = parse_token(token)
        # token过期或者无效
        if payload is None:
            return Response(
                {"status": "error", "message": "Token expired or invalid"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(
            {"status": "success", "message": "Token is valid"},
            status=status.HTTP_200_OK,
        )
class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.MATA.get("HTTP_AUTHORIZATION")
        if refresh_token is None:
            return Response(
                {"status": "error", "message": "No refresh token provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payload = parse_token(refresh_token)
        if payload is None:
            return Response(
                {"status": "error", "message": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        user_id = payload["user_id"]
        # access_token生成
        expiration_time = timezone.now() + timezone.timedelta(minutes=5)
        payload = {
            "user_id": user_id,
            "exp": expiration_time,
        }
        access_token = jwt.encode(payload, "secret_code", algorithm="HS256")
        return Response(
            {"access_token": access_token},
        )



# 登录，已完成测试
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
            # access_token生成
            expiration_time = timezone.now() + timezone.timedelta(minutes=5)
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


# 使用验证码注册，已完成测试
class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        verificationCode = request.data.get("verificationCode")
        # 验证用户名是否已经存在
        if User.objects.filter(username=username).exists():
            return Response(
                {"message": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 验证邮箱格式
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            return Response(
                {"message": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST
            )
        # 验证邮箱是否已经存在
        if User.objects.filter(email=email).exists():
            return Response(
                {"message": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST
            )
        code = VerificationCode.objects.get(email=email)
        # 验证码不存在
        if code is None:
            return Response(
                {"message": "Verification code does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 验证码不匹配
        if code.code != verificationCode:
            return Response(
                {"message": "Verification code is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 验证码过期
        if code.is_expired():
            return Response(
                {"message": "Verification code has expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.create_user(
            username=username, password=password, email=email
        )
        # 返回注册成功的信息和用户ID
        return Response(
            {"message": "User registered successfully", "user_id": user.id},
            status=status.HTTP_201_CREATED,
        )


# 发送注册验证码 ，已完成测试
class SendCodeView(APIView):
    def post(self, request):
        email = request.data.get("email")
        # 验证邮箱格式
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            return Response(
                {"message": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST
            )
        # 验证邮箱是否存在
        if User.objects.filter(email=email).exists():
            return Response(
                {"status": "error", "message": "Email already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 生成验证码并保存
        verificationCode = VerificationCode()
        code = verificationCode.create_code(email)
        # 发送验证码到邮箱
        send_mail(
            recipient_list=[email],
            subject="验证码",
            body="尊敬的影云用户(" + email + ")您好，您的验证码如下: " + code,
        )
        # 返回发送成功的信息和验证码
        return Response(
            {"status": "success", "message": "Verification code sent"},
            status=status.HTTP_200_OK,
        )


# 获取用户信息,已完成测试，可以通过返回的URL直接访问头像
class UserInfoView(APIView):
    def post(self, request):
        # 验证用户身份
        token = request.data.get("token")
        if not token:
            return Response(
                {"message": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        payload = parse_token(token)
        if not payload:
            return Response(
                {"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
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
            },
            status=status.HTTP_200_OK,
        )


# 登出
class LoginOutView(APIView):
    def post(self, request):
        refresh_token = request.META.get("HTTP_REFRESH_TOKEN")
        access_token = request.META.get("HTTP_ACCESS_TOKEN")
        if not refresh_token or not access_token:
            return Response(
                {"message": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        cache.set(refresh_token, True, 604800)
        cache.set(access_token, True, 300)
        return Response({"message": "Logout successfully"}, status=status.HTTP_200_OK)


# 忘记密码
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
