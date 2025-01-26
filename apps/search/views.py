from django.http import JsonResponse
from rest_framework.views import APIView
from apps.images.models import Image, ImageTag
from datetime import datetime
# Create your views here.

class SelectImagesByTime(APIView):
    # 按时间搜索,格式：2025-08-20
    def post(self, request, *args, **kwargs):
        # 识别搜素模式（按）
        userid = request.data.get("user_id")
        time = request.data.get("time")
        selectTime = datetime.strptime(time, "%Y-%m-%d").date()

        # print("********************************************************")
        # print(request.data)
        # print("********************************************************")

        # # 按时间搜索
        images = Image.objects.filter(user_id=userid, time__date=selectTime)
        images_url = [image.url for image in images]
        images_id = [image.id for image in images]
        return JsonResponse({
            "state": "success",
            'images_url': images_url,
            'images_id': images_id,
        })

class SelectImagesByPosition(APIView):
    # 按地点搜索
    def post(self, request, *args, **kwargs):
        userid = request.data.get("user_id")
        selectPosition = request.data.get("position")

        # print("********************************************************")
        # print(request.data)
        # print("********************************************************")

        # # 按时间搜索
        images = Image.objects.filter(user_id=userid, position=selectPosition)
        images_url = [image.url for image in images]
        images_id = [image.id for image in images]
        return JsonResponse({
            "state": "success",
            'images_url': images_url,
            'images_id': images_id,
        })
        pass

class SelectImagesByTags(APIView):
    # 按照标签搜索图片
    def post(self, request, *args, **kwargs):
        userid = request.data.get("user_id")
        tagslist = request.data.get("tags")

        print("********************************************************")
        print(request.data)
        print("********************************************************")

        urlSet = set()
        idSet = set()

        for tag_name in tagslist:
            image_ids = ImageTag.objects.filter(tag_name=tag_name).values_list('image_id', flat=True)
            images = Image.objects.filter(user_id=userid, id__in=image_ids)
            urls = [image.url for image in images]
            ids = [image.id for image in images]
            urlSet.update(urls)
            idSet.update(ids)

        urlList = list(urlSet)
        idList = list(idSet)

        return JsonResponse({
            "state": "success",
            "urls": urlList,
            "ids": idList ,
        })

