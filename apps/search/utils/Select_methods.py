import calendar
from datetime import datetime

from apps.images.models import Image, ImageTag
import requests
from apps.search.utils.Cosine_similarity import cos_similarity


def select_by_userid(user_id):
    images = Image.objects.filter(user_id=user_id)
    return images


def select_by_time(images, time):
    """
    按时间搜索（可具体到年、月、日）
    """
    num = time.count("-")

    # 只输入年份
    if num == 0:
        images = images.filter(time__year=time)
    elif num == 1:
        year = int(time.split("-")[0])
        month = int(time.split("-")[1])
        image_list = images.filter(time__year=year)
        images = []
        for image in image_list:
            if image.time.month == month:
                images.append(image)
    else:
        year = int(time.split("-")[0])
        month = int(time.split("-")[1])
        day = int(time.split("-")[2])
        image_list = images.filter(time__year=year)
        images = []
        for image in image_list:
            if image.time.month == month and image.time.day == day:
                images.append(image)

    images_url = [image.url for image in images]
    images_id = [image.id for image in images]

    return images_id, images_url, images


def get_datetime(time, pattern):
    global time1
    print(time)
    num = time.count("-")
    if num == 0:
        if pattern == 1:
            time1 = datetime(int(time), 1, 1)
        else:
            time1 = datetime(int(time), 12, 31)
    elif num == 1:
        if pattern == 1:
            time1 = datetime(int(time.split("-")[0]), int(time.split("-")[1]), 1)
        else:
            _, num_days = calendar.monthrange(
                int(time.split("-")[0]), int(time.split("-")[1])
            )
            time1 = datetime(int(time.split("-")[0]), int(time.split("-")[1]), num_days)
    elif num == 2:
        if pattern == 1:
            time1 = datetime(
                int(time.split("-")[0]),
                int(time.split("-")[1]),
                int(time.split("-")[2]),
            )
        else:
            time1 = datetime(
                int(time.split("-")[0]),
                int(time.split("-")[1]),
                int(time.split("-")[2]),
                23,
                59,
                59,
            )
    return time1


def select_by_timezone(images, start_time, end_time):
    """
    按时间范围查找
    """
    time1 = get_datetime(start_time, 1)
    time2 = get_datetime(end_time, 2)

    images = images.filter(time__range=(time1, time2))

    ids = [image.id for image in images]
    urls = [image.url for image in images]

    return ids, urls, images


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


def select_by_tags(images, tags_list):
    # 获取所有符合条件的图片的 URL 和 ID
    image_ids = ImageTag.objects.filter(tag_name__in=tags_list).values_list(
        "image_id", flat=True
    )
    images = images.filter(id__in=image_ids)
    urls = set(image.url for image in images)
    ids = set(image.id for image in images)

    # 计算所有标签的交集
    for tag_name in tags_list:
        tag_image_ids = ImageTag.objects.filter(tag_name=tag_name).values_list(
            "image_id", flat=True
        )
        tag_image_urls = set(
            image.url for image in Image.objects.filter(id__in=tag_image_ids)
        )
        tag_image_ids = set(
            image.id for image in Image.objects.filter(id__in=tag_image_ids)
        )

        # 更新交集
        urls &= tag_image_urls
        ids &= tag_image_ids

    # 将结果转换为列表
    urlList = list(urls)
    idList = list(ids)

    return urlList, idList, images


def select_by_description(images, description):

    description_list = [image.description for image in images]

    similarityList = []
    for sentence in description_list:
        similarity = cos_similarity(sentence, description)
        similarityList.append(similarity)

    similarity_scores = [similarityList]

    print(similarity_scores)

    # 将相似度与图片关联
    image_similarity_pairs = [
        (images[i], similarity_scores[0][i]) for i in range(len(images))
    ]

    # 过滤出余弦相似度大于0.1的图片
    filtered_images = [pair for pair in image_similarity_pairs if pair[1] > 0.1]

    # 按照相似度从高到低排序
    filtered_images.sort(key=lambda x: x[1], reverse=True)

    # 获取排序后的图片列表（返回url和id）
    result = [
        {"image_id": image.id, "image_url": image.url} for image, _ in filtered_images
    ]

    idList = [item["image_id"] for item in result]
    urlList = [item["image_url"] for item in result]

    return idList, urlList, filtered_images
