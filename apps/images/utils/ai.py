from .ai_utils.common import get_access_token
from .ai_utils.common import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
)
import requests
import logging
import openai

logger = logging.getLogger("django")


# ------------------------------------   图像内容审核  -------------------------------
def content_filter(image_base64):
    # 获取Access Token
    access_token = get_access_token()

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

    # logger.debug(f"Response: {response.text}")
    # 解析响应结果
    reason = "合规"
    result = None

    # 使用 response.json() 获取 JSON 数据
    try:
        response_json = response.json()
        result = response_json.get("conclusion")  # 获取结论
        if result == "不合规":
            reason = response_json["data"][0].get("msg")  # 获取原因
    except ValueError:
        # 如果响应不是有效的 JSON，可以处理异常
        reason = "响应内容不是有效的JSON"

    return result, reason


# ------------------------------------------------------------------------------


# -------------------------------------- 图像理解 -------------------------------
def image_understanding(image_base64):
    url = (
        "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general?access_token="
        + get_access_token()
    )

    payload = f"image={image_base64}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    response = requests.post(url, headers=headers, data=payload.encode("utf-8"))

    # 使用 response.json() 获取 JSON 数据
    try:
        response = response.json()
    except ValueError:
        # 如果响应不是有效的 JSON，可以处理异常
        logger.error("响应内容不是有效的JSON")
        return ["响应内容不是有效的JSON"]
    # 提取所有的 keyword
    keywords = [item["keyword"] for item in response["result"]]
    return keywords


# --------------------------------------------------------------------------------


# ------------------------------------- 图像描述 -----------------------------------
openai.api_key = OPENAI_API_KEY
openai.base_url = OPENAI_BASE_URL


def image_description(image_base64):
    # 假设使用支持图像输入的 API
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "用一句话描述一下这个图片。"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            }
        ],
        max_tokens=100,
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------------


# ------------------------------------- 图像分类 ----------------------------------
def image_classification(image_base64):
    pass


# --------------------------------------------------------------------------------
