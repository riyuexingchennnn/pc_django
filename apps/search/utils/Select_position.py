import requests


def select_by_position(image_list, position):

    images = []
    # 你的高德地图API Key
    API_KEY = "***REMOVED***"

    url = f"https://restapi.amap.com/v3/geocode/geo?key={API_KEY}&address={position}"

    response = requests.get(url)

    print(response.json())

    if response.status_code == 200:
        json = response.json()
        print(json["geocodes"][0]["level"])
        if json["geocodes"][0]["level"] == "省":
            for image in image_list:
                url1 = f"https://restapi.amap.com/v3/geocode/geo?key={API_KEY}&address={image.position}"
                response1 = requests.get(url1)
                if (
                    response1.json()["geocodes"][0]["province"]
                    == json["geocodes"][0]["province"]
                ):
                    images.append(image)
        elif json["geocodes"][0]["level"] == "市":
            for image in image_list:
                url1 = f"https://restapi.amap.com/v3/geocode/geo?key={API_KEY}&address={image.position}"
                response1 = requests.get(url1)
                if (
                    response1.json()["geocodes"][0]["city"]
                    == json["geocodes"][0]["city"]
                    and response1.json()["geocodes"][0]["province"]
                    == json["geocodes"][0]["province"]
                ):
                    images.append(image)
            pass
        elif json["geocodes"][0]["level"] == "区县":
            for image in image_list:
                url1 = f"https://restapi.amap.com/v3/geocode/geo?key={API_KEY}&address={image.position}"
                response1 = requests.get(url1)
                if (
                    response1.json()["geocodes"][0]["city"]
                    == json["geocodes"][0]["city"]
                    and response1.json()["geocodes"][0]["province"]
                    == json["geocodes"][0]["province"]
                    and response1.json()["geocodes"][0]["district"]
                    == json["geocodes"][0]["district"]
                ):
                    images.append(image)
        else:
            # 区域太小
            pass

    images_url = [image.url for image in images]
    images_id = [image.id for image in images]

    return images_id, images_url, images
