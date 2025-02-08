from django.http import JsonResponse
from rest_framework.views import APIView
from apps.images.models import Image, ImageTag
from apps.search.utils.Select_time import select_by_time
from apps.search.utils.Select_tag import select_by_tags
from apps.search.utils.Select_description import select_by_description
from apps.search.utils.Select_userid import select_by_userid

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
        userid = request.data.get("user_id")
        selectPosition = request.data.get("position")

        # 按地点搜索
        images = Image.objects.filter(user_id=userid, position=selectPosition)
        images_url = [image.url for image in images]
        images_id = [image.id for image in images]
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
            _, _, images = images.filter(position=position)

        url1 = set(image.url for image in images)
        id1 = set(image.id for image in images)

        if len(tags_list) != 0:
            # 将结果转换为列表
            urls, ids, _ = select_by_tags(
                select_by_userid(user_id=user_id), tags_list=tags_list
            )
            urlList = list(set(urls) & url1)
            idList = list(set(ids) & id1)

        else:
            urlList = list(url1)
            idList = list(id1)

        return JsonResponse(
            {"state": "success", "image_id": idList, "image_url": urlList}
        )
