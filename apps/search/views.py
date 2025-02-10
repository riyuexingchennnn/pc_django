from django.http import JsonResponse
from rest_framework.views import APIView
from apps.search.utils.Select_methods import (
    select_by_userid,
    select_by_time,
    select_by_position,
    select_by_tags,
    select_by_description,
)

# Create your views here.


class SelectImagesByTime(APIView):
    # 按时间搜索,格式：2025-08-20
    def post(self, request, *args, **kwargs):
        # 识别搜素模式（按时间搜索）
        user_id = request.data.get("user_id")
        time = request.data.get("time")

        images_id, images_url, _ = select_by_time(
            select_by_userid(user_id=user_id), time=time
        )

        return JsonResponse(
            {
                "state": "success",
                "image_id": images_id,
                "image_url": images_url,
            }
        )


class SelectImagesByPosition(APIView):
    # 按地点搜索
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        position = request.data.get("position")

        images_id, images_url, _ = select_by_position(
            select_by_userid(user_id=user_id), position=position
        )
        return JsonResponse(
            {
                "state": "success",
                "image_url": images_url,
                "image_id": images_id,
            }
        )
        pass


class SelectImagesByTags(APIView):
    # 按照标签搜索图片
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        tags_list = request.data.get("tags")

        urlList, idList, _ = select_by_tags(
            select_by_userid(user_id=user_id), tags_list=tags_list
        )

        return JsonResponse(
            {
                "state": "success",
                "image_url": urlList,
                "image_id": idList,
            }
        )


class SelectImagesByDescription(APIView):
    # 按描述搜索
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        description = request.data.get("description")

        idList, urlList, _ = select_by_description(
            select_by_userid(user_id=user_id), description=description
        )

        return JsonResponse(
            {"state": "success", "image_id": idList, "image_url": urlList}
        )


class SelectImagesByTPTD(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        time = request.data.get("time")
        position = request.data.get("position")
        tags_list = request.data.get("tags")

        # 获取用户全部照片
        images = select_by_userid(user_id=user_id)

        # 按时间筛选
        if time != "":
            pass
            _, _, images = select_by_time(images=images, time=time)

        # 按地点筛选
        if position != "":
            _, _, images = select_by_position(image_list=images, position=position)

        url1 = set(image.url for image in images)
        id1 = set(image.id for image in images)

        if len(tags_list) != 0:
            # 将结果转换为列表
            urls, ids, _ = select_by_tags(
                select_by_userid(user_id=user_id), tags_list=tags_list
            )
            urlList = list(set(urls) & set(url1))
            idList = list(set(ids) & set(id1))

        else:
            urlList = list(url1)
            idList = list(id1)

        return JsonResponse(
            {"state": "success", "image_id": idList, "image_url": urlList}
        )


class SelectImages(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        message = request.data.get("message")

        images = select_by_userid(user_id=user_id)
        if len(images) == 0:

            pass

        ids = [image.id for image in images]
        urls = [image.url for image in images]

        return JsonResponse(
            {
                "state": "success",
                "ids": ids,
                "urls": urls,
            }
        )
