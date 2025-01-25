import base64
import urllib
import requests

# ---------------------- 以下为API常量 --------------------------
OPENAI_API_KEY = "***REMOVED***"
OPENAI_BASE_URL = "https://api.chatanywhere.tech"

BAIDU_API_KEY = "***REMOVED***"
BAIDU_SECRET_KEY = "***REMOVED***"


# ---------------------- 以下为辅助函数 --------------------------
def get_file_content_as_base64(path, urlencoded=False):
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded
    :return: base64编码信息
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content


def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": BAIDU_API_KEY,
        "client_secret": BAIDU_SECRET_KEY,
    }
    response = requests.post(url, params=params)
    token = response.json().get("access_token")
    if token:
        return token
    else:
        raise Exception("Failed to get access token")


# ------------------------------------------------------------------
