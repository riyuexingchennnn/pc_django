import base64
import urllib
import requests
import os
import json

# views.py
import logging

# 获取日志记录器
logger = logging.getLogger("django")

API_KEY = "***REMOVED***"
SECRET_KEY = "***REMOVED***"

# ------------------------------- 内容审核API --------------------------------------
def content_filter(image_path):
    # 获取Access Token
    access_token = get_access_token()

    # 确保图片文件存在
    if not os.path.exists(image_path):
        # 尽量用python自带的异常机制来处理错误，而不是用print()
        raise OSError(f"图片文件 {image_path} 不存在！")

    # 获取图片的base64编码
    image_base64 = get_file_content_as_base64(image_path, urlencoded=True)

    # 打印Base64编码的前100个字符，确认是否正确
    # print(f"Base64 Encoded Image: {image_base64[:100]}...")  # 打印前100个字符

    # 拼接API URL
    url = f"https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/v2/user_defined?access_token={access_token}"

    # 构建请求参数
    payload = f"image={image_base64}"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    # 发起POST请求
    response = requests.post(url, headers=headers, data=payload.encode("utf-8"))

    logger.info(f"内容审核API返回结果: {response.text}")
    # 解析 JSON 数据
    data = json.loads(response.text)

    # 提取是否合规
    is_compliant = data.get("conclusion", "未知")  # 取 "conclusion" 字段
    # 输出结果
    logger.info(f"是否合规: {is_compliant}")
    if is_compliant == "不合规":
        # 提取不合规的理由
        non_compliant_reasons = [
            item.get("msg", "无理由") for item in data.get("data", [])
        ]
        logger.info(f"不合规的理由: {', '.join(non_compliant_reasons)}")
        return is_compliant, non_compliant_reasons
    else:
        return is_compliant, None


# -------------------------------------------------------------------------------


# -------------------------------- 图片分类 --------------------------------------
# 暂时不写，考虑使用GoogleNet
def image_classification():
    pass


# -------------------------------------------------------------------------------


# ------------------------------- 图像理解API -------------------------------------
def image_understanding(image_path):
    # 确保图片文件存在
    if not os.path.exists(image_path):
        # 尽量用python自带的异常机制来处理错误，而不是用print()
        raise OSError(f"图片文件 {image_path} 不存在！")

    url = (
        "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general?access_token="
        + get_access_token()
    )

    # 使用 get_file_content_as_base64 方法获取图像的 Base64 编码
    payload = {
        "image": get_file_content_as_base64(image_path, False),
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, headers=headers, data=payload)

    logger.info(f"图像理解API返回结果: {response.text}")
    # 提取所有的 keyword
    keywords = [item["keyword"] for item in response.text["result"]]
    return keywords


# -------------------------------------------------------------------------------


# ------------------------------- 图片描述API ------------------------------------
def image_captioning(image_path):
    pass


# -------------------------------------------------------------------------------


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
        "client_id": API_KEY,
        "client_secret": SECRET_KEY,
    }
    response = requests.post(url, params=params)
    token = response.json().get("access_token")
    if token:
        return token
    else:
        raise Exception("Failed to get access token")


# ------------------------------------------------------------------
