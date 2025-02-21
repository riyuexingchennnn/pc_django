import json

import requests

API_KEY = "4a85d027214c8fdbf9003564a0cc7da4"
position = "中国"
url = f"https://restapi.amap.com/v3/config/district?key={API_KEY}&keywords=中国&subdistrict=3&extensions=base"

# 获取网页上的JSON数据
response = requests.get(url)

# 判断请求是否成功
if response.status_code == 200:
    # 解析JSON数据
    data = response.json()

    # 将数据保存到本地 Python 文件中，不转义非ASCII字符
    with open("data.py", "w", encoding="utf-8") as f:
        f.write(f"data = {json.dumps(data, ensure_ascii=False, indent=4)}")
    print("数据已成功保存到data.py")
else:
    print("请求失败，状态码：", response.status_code)
