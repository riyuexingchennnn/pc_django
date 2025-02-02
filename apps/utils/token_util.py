from django.core.cache import cache
import jwt


# token验证，已经完成测试, 为了其他模块复用，单独提出来
def parse_token(token):
    # 检查是否在黑名单缓存中（用来实现登出功能）
    if cache.get(token):
        return None
    try:
        # 使用相同的密钥进行解码
        payload = jwt.decode(token, "secret_code", algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        # 如果token过期
        return None
    except jwt.InvalidTokenError:
        # 如果token无效
        return None
