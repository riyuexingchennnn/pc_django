from django.http import JsonResponse
from rest_framework.views import APIView
from apps.search.utils.Select_methods import (
    select_by_userid,
    select_by_time,
    select_by_position,
    select_by_tags,
    select_by_description,
    select_by_timezone,
)
from apps.images.models import ImageTag

# Create your views here.


class SelectImagesByTime(APIView):
    # 按时间搜索,格式：2025-08-20
    def post(self, request, *args, **kwargs):
        # 识别搜素模式（按时间搜索）
        user_id = request.data.get("user_id")
        time = request.data.get("time")

        images_id, images_url, images = select_by_time(
            select_by_userid(user_id=user_id), time=time
        )

        if len(images) != 0:
            return JsonResponse(
                {
                    "state": "success",
                    "image_id": images_id,
                    "image_url": images_url,
                }
            )
        else:
            return JsonResponse(
                {
                    "state": "failed",
                    "message": "未找到这个时间的图片",
                }
            )


class SelectImagesByTimeZone(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        start_time = request.data.get("starttime")
        end_time = request.data.get("endtime")

        ids, urls, images = select_by_timezone(
            select_by_userid(user_id=user_id), start_time=start_time, end_time=end_time
        )

        if len(images) != 0:
            return JsonResponse(
                {
                    "state": "success",
                    "ids": ids,
                    "urls": urls,
                }
            )
        else:
            return JsonResponse(
                {
                    "state": "failed",
                    "message": "未找到这个时间段的图片",
                }
            )


class SelectImagesByPosition(APIView):
    # 按地点搜索
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        position = request.data.get("position")

        images_id, images_url, images = select_by_position(
            select_by_userid(user_id=user_id), position=position
        )

        if len(images) != 0:
            return JsonResponse(
                {
                    "state": "success",
                    "image_url": images_url,
                    "image_id": images_id,
                }
            )
        else:
            return JsonResponse(
                {
                    "state": "failed",
                    "message": "未找到这个地点的图片",
                }
            )


class SelectImagesByTags(APIView):
    # 按照标签搜索图片
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        tags_list = request.data.get("tags")

        urlList, idList, images = select_by_tags(
            select_by_userid(user_id=user_id), tags_list=tags_list
        )

        if len(images) != 0:
            return JsonResponse(
                {
                    "state": "success",
                    "image_url": urlList,
                    "image_id": idList,
                }
            )
        else:
            return JsonResponse(
                {
                    "state": "failed",
                    "message": "未找到带有这些标签的图片",
                }
            )


class SelectImagesByDescription(APIView):
    # 按描述搜索
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        description = request.data.get("description")

        idList, urlList, images = select_by_description(
            select_by_userid(user_id=user_id), description=description
        )

        if len(images) != 0:
            return JsonResponse(
                {"state": "success", "image_id": idList, "image_url": urlList}
            )
        else:
            return JsonResponse(
                {
                    "state": "failed",
                    "message": "未找到与描述的图片",
                }
            )


class SelectImagesByTPT(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        start_time = request.data.get("starttime")
        end_time = request.data.get("endtime")
        position = request.data.get("position")
        tags_list = request.data.get("tags")

        # 获取用户全部照片
        images = select_by_userid(user_id=user_id)

        # 按时间筛选
        if start_time != "" and end_time != "":
            _, _, images = select_by_timezone(
                images=images, start_time=start_time, end_time=end_time
            )

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

        if len(idList) != 0 and len(urlList) != 0:
            return JsonResponse(
                {"state": "success", "image_id": idList, "image_url": urlList}
            )
        else:
            return JsonResponse(
                {
                    "state": "failed",
                    "message": "未找到相关图片",
                }
            )


class SelectImages(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        message = request.data.get("message")

        images = select_by_userid(user_id=user_id)
        # 判断是否为地点
        _, _, images = select_by_position(images, position=message)
        if len(images) == 0:
            # 判断是否为时间
            mes = str(message).replace(".", "-")
            _, _, images = select_by_time(images, time=mes)
            if len(images) == 0:
                tags = [
                    image.tag_name for image in ImageTag.objects.filter(user_id=user_id)
                ]

        ids = [image.id for image in images]
        urls = [image.url for image in images]

        if len(images) != 0:
            return JsonResponse(
                {
                    "state": "success",
                    "ids": ids,
                    "urls": urls,
                }
            )
        else:
            return JsonResponse(
                {
                    "state": "failed",
                    "message": "未找到相关图片",
                }
            )


class GetTags(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        images = select_by_userid(user_id=user_id)
        image_ids = [image.id for image in images]
        tagList = []
        for id in image_ids:
            imageList = ImageTag.objects.filter(image_id=id)
            tags = [image.tag_name for image in imageList]
            tagList.extend(tags)

        tagList = set(tagList)

        # 将集合转换回列表
        tagList = list(tagList)

        return JsonResponse({"tags": tagList})
