from rest_framework.views import APIView
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
import traceback
from django.http import JsonResponse
from django.http import HttpResponse
import uuid
import logging

logger = logging.getLogger("django")


# def choosePatten(request):
#     # 进入支付选择页面
#
#     pass


class AlipayView(APIView):
    # 支付请求
    def post(self, request, *args, **kwargs):
        # 支付宝配置
        alipay_client_config = AlipayClientConfig()
        alipay_client_config.server_url = (
            "https://openapi-sandbox.dl.alipaydev.com/gateway.do"
        )
        alipay_client_config.app_id = "9021000143656585"
        alipay_client_config.app_private_key = "MIIEowIBAAKCAQEAkI5gngsSVGTmpx+20xqgDnTv7lgEgrLjwniggjSaDCgA7idwBcRgosQrIupSD9Oo3lp1F3B2rORMMB8oBrwCHcGOK3++juiMWuAfM5mGxRZauQB8XVVBBNmMrkjljwubRCV7akT0GdYmsmOFT8aC4OOVuwhcwHsaNd329xYHAUIwdb1yUpo3z/6S5CLPR9vqFwDKnRyu5yoqgawIErM+Yd2o/np+bFZo0H0GIm5W4P6mgIRtYnnamHBIBynCxmGYWH0o/DpXGE/ynykADXUD43SzyLvjVliPQhz2/Al7GhZEuZOxVPCGi2ye6ucB7QvPN7HdoQs5PVVvBUe8qa0apQIDAQABAoIBAH3FIpLfFyeOUo/9q9eoRrHNVCOPOP1uH3PH9/7RPWZuN8D9Vx3tahazjsRmEtfqU/aBxXaLRvXN++uyb+TMFxtEmCmIj4dPFS7L6NnALd20QWLM5WdfEZ7imN/aVMBMXN7BrcscCzWfeTOkGwz5rk10NYXxFKHzeS583K7F33pbg5esbjTBc/YltL6mg1Ck9vjM5HgfOcEqSZjT1kanPTMwmJ30Ezm18fHFVnp/6R/161lbW9+VFfCiYAMxxwNliIf9WatR/L02EgjRzR7PoCxbTEJFdkyFTsCms74zMeBZTb42xNTjezT5k1BnG2/SMf46rfLGX5q5lkxAx70TYIECgYEA6CsD+Qdq8jIjFnv4icHLXZd1DSgKOK9RcRZiMv1rCkWej5pKXx6pCUYwXstCNdJlMSro3CxwCCZIW+Sm1d8RyOpMWqF88uVoaCGAELwi9FrZtZOUdWZ+lwOt1b31o9a9VeYCCa36EwnhAOycQp/r17r2teAu4CUpWJpYNaZbLwkCgYEAn2UR1vXh/ik+n1pN7bW5vRYX7+81wo72r0/3iDWHZouQWEVeLkp1F6vQPDxwcgPYti+qvJqVlkt4wE8KbmE/jtzFdcL5HxkDc7ltSRujj7jmBXSzqmmha9pFu8W0qO6Rh3Ddu1q1gy6OHLNNzQte/kqo0ZlwrOuX9dm5+ZAHmb0CgYANOW4HgFGqLArtm/AjQKOp2Be1wSMb6XiVHXZIe0Dem+qVOW+lDWUJfzMAI0nJMQvMiioraGiVPkD+4v5Rzlv/+sCQpQQt/b09uTLHQUAodQhTnG1nZogtZ+s98o0MYQ31150kGgHVlcl4OQIJlXxklGS7JWLmJ5e8UUZW//vPqQKBgB0VXfnxB3lOoUSGP63d+LQNsfRvm0mSuGQonSvXSItnb8ELdzHPGCpniSlUhdfn58TmUar0MdMoljHQukCFsgkpM0ZXewk3kS+uZ8htKJzyydW5A4dWmsOJIiwu2NXyIc+qwmqLFI+JERkfhlShfIW9rawA6VRD8IhFX++vXhOpAoGBAJPnxYsEV87z9ac9ipOY5jxO+wMVDpCeMTIXEtmcqzAaT6oMgpZlkPpoyCLpP7YXeV67LfEBTIQOO24H55stxBWu65CJOgbGZeuEAvtd7ERuWtAdLrKCSXRzukv9uvlbkLA11C8+CiAN78RdN64uPVV4ZweRroEbtYMlU6vgffsb"
        alipay_client_config.alipay_public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAhp9yBgwPyObTL9Adm1wgiWJJS6XDtstVWjzia9uDS+8rvA7RUdJJvPVqDOQgukwqTOWksl4UX8o7UmDj2x9uBRtu71E1duk41yBPWk0EpPJnDt/SjPyxg0zl//xGjSRK2Lvu4V6+hTRuRbuRego6v5AE82pCXSKLT2YFvRwB/Oxki5GXRvdmPlFElvwZ+s2uBCME4C/xEkGgsrZ+q1Ohn9cU03xDy19UJDz9sbhwFfaAJfUXqdyQRKTAGBUwamyWpMe1pg0iNkGL2RIwlRQTWTHGDC1amIwOj1OoNO2xpjtwqhvet7oDE8VKKuBGswOllunkUp3diGrUZxQs01JkJQIDAQAB"

        client = DefaultAlipayClient(alipay_client_config)

        # 获取套餐
        pattern = request.data.get("pattern")

        # pattern = '1'
        uuid1 = uuid.uuid1()
        out_trade_no = str(uuid1)

        # print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        # print(uuid1)
        # print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')

        try:
            if pattern == "1":
                # 获取订单信息
                subject = "套餐1"
                total_amount = "10.00"
            else:
                # 获取订单信息
                subject = "套餐2"
                total_amount = "20.00"
            # 构造支付请求模型
            model = AlipayTradePagePayModel()
            model.out_trade_no = out_trade_no
            model.total_amount = total_amount
            model.subject = subject
            model.product_code = "FAST_INSTANT_TRADE_PAY"
            # 创建支付请求
            request_data = AlipayTradePagePayRequest(biz_model=model)
            request_data.return_url = (
                "http://localhost:8000/pay/alipay"  # 支付完成后的跳转页面
            )
            request_data.notify_url = (
                "http://localhost:8000/pay/alipay/notify"  # 异步通知地址
            )

            # 调用支付宝接口
            response_content = client.page_execute(request_data, http_method="GET")
            return JsonResponse(
                {"payment_url": response_content, "trade_no": out_trade_no}
            )

        except Exception as e:
            return (
                JsonResponse({"error": str(e), "traceback": traceback.format_exc()}),
                500,
            )

    # 支付宝返回函数
    def get(self, request, *args, **kwargs):
        # 向数据库中保存相关数据

        # print('..............................................')
        # print(request.GET.get('out_trade_no'))
        # print('..............................................')
        method = request.method
        return HttpResponse(method + "支付成功")


# def alipay_notify(request):
#     return HttpResponse("异步通知接收成功")
