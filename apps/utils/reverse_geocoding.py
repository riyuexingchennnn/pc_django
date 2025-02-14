import requests


def reverse_geocoding(longitude, latitude):
    """
    输入：
        longitude：精度  例：116.481488
        latitude：纬度   例：39.990464
    """
    API_KEY = "***REMOVED***"
    url = f"https://restapi.amap.com/v3/geocode/regeo?key={API_KEY}&location={longitude},{latitude}&poitype=&radius=0&extensions=base&roadlevel=1"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(data)
        if data["status"] == "1":
            province = data["regeocode"]["addressComponent"]["province"]
            city = data["regeocode"]["addressComponent"]["city"]
            district = data["regeocode"]["addressComponent"]["district"]

            if len(city) == 0:
                if province == "北京市":
                    city = "北京城区"
                elif province == "上海市":
                    city = "上海城区"
                elif province == "天津市":
                    city = "天津城区"
                else:
                    if district in [
                        "巫溪县",
                        "奉节县",
                        "彭水苗族土家族自治县",
                        "秀山土家族苗族自治县",
                        "石柱土家族自治县",
                        "巫山县",
                        "丰都县",
                        "城口县",
                        "忠县",
                        "垫江县",
                        "云阳县",
                        "酉阳土家族苗族自治县",
                    ]:
                        city = "重庆郊县"
                    else:
                        city = "重庆城区"

            position = str(province + city + district)

            return position
    else:
        print("访问失败，请检查输入并重试")
