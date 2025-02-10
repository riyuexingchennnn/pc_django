import uuid
from django.http import HttpResponse
from rest_framework.views import APIView
import qrcode
import io

# Create your views here.


class QRcodeView(APIView):
    def get(self, request, *args, **kwargs):
        id = uuid.uuid1()
        data = str(id).replace("-", "")
        qr_img = qrcode.make(data)

        img_io = io.BytesIO()
        qr_img.save(img_io, "PNG")
        img_io.seek(0)
        return HttpResponse(img_io, content_type="image/png")
