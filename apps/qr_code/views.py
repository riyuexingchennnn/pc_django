import base64
import uuid
from django.http import JsonResponse
from rest_framework.views import APIView
import qrcode
import io
from apps.qr_code.models import QRcodeId, TemporaryToken
from apps.accounts.models import User
from apps.utils.token_util import parse_token


# Create your views here.


class QRcodeView(APIView):
    def get(self, request, *args, **kwargs):
        id = uuid.uuid1()
        data = str(id).replace("-", "")
        qr_img = qrcode.make(data)

        img_io = io.BytesIO()
        qr_img.save(img_io, "PNG")
        img_io.seek(0)

        img_base64 = base64.b64encode(img_io.getvalue()).decode("utf-8")

        QRcodeId.objects.create(
            qrcode_id=data,
        )

        # 创建一个字典包含图片和数据
        response_data = {
            "image": img_base64,  # 图片的 Base64 编码数据
            "data": data,  # 其他字符串数据
        }

        return JsonResponse(response_data)


class QRcodeStateView(APIView):
    def post(self, request, *args, **kwargs):
        qrcode_id = request.data.get("qrcode_id")
        item = QRcodeId.objects.filter(qrcode_id=qrcode_id).first()
        if item.state != "used":
            return JsonResponse({"state": str(item.state)})
        else:
            item.state = "stop"
            item.save()
            item2 = TemporaryToken.objects.filter(qrcode_id=qrcode_id).first()
            user_id = item2.user
            user = User.objects.filter(id=user_id).first()
            email = user.email
            password = user.password
            return JsonResponse(
                {
                    "state": "used",
                    "email": email,
                    "password": password,
                }
            )


class PhoneScanned(APIView):
    def post(self, request, *args, **kwargs):
        token = request.META.get("HTTP_AUTHORIZATION")
        payload = parse_token(token)
        user_id = payload.get("user_id")
        # user_id = request.data.get("user_id")
        qrcode_id = request.data.get("qrcode_id")

        # 修改二维码状态
        item = QRcodeId.objects.filter(qrcode_id=qrcode_id).first()
        item.state = "scanned"
        item.save()

        id = uuid.uuid1()
        temporary_token = str(id).replace("-", "")

        TemporaryToken.objects.create(
            temporary_token=temporary_token, qrcode_id=qrcode_id, user=user_id
        )

        return JsonResponse({"temporary_token": temporary_token})


class QRcodeLoginView(APIView):
    def post(self, request, *args, **kwargs):
        temporary_token = request.data.get("temporary_token")
        item1 = TemporaryToken.objects.filter(temporary_token=temporary_token).first()

        user_id = item1.user
        qrcode_id = item1.qrcode_id

        item2 = QRcodeId.objects.filter(qrcode_id=qrcode_id).first()
        item2.state = "used"
        item2.save()

        return JsonResponse({"state": "success"})
