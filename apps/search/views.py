from django.http import JsonResponse
from rest_framework.views import APIView
from apps.images.models import Image, ImageTag
from datetime import datetime
from apps.search.utils.Cosine_similarity import cos_similarity


# Create your views here.


class SelectImagesByTime(APIView):
    # 按时间搜索,格式：2025-08-20
    def post(self, request, *args, **kwargs):
        # 识别搜素模式（按时间搜索）
        userid = request.data.get("user_id")
        time = request.data.get("time")
        selectTime = datetime.strptime(time, "%Y-%m-%d").date()

        # print("********************************************************")
        # print(request.data)
        # print("********************************************************")

        # # 按时间搜索
        images = Image.objects.filter(user_id=userid, time__date=selectTime)
        # print(images)
        images_url = [image.url for image in images]
        images_id = [image.id for image in images]
        return JsonResponse(
            {
                "state": "success",
                "image_url": images_url,
                "image_id": images_id,
            }
        )


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
        userid = request.data.get("user_id")
        tagslist = request.data.get("tags")

        print("********************************************************")
        print(request.data)
        print("********************************************************")

        # 获取所有符合条件的图片的 URL 和 ID
        image_ids = ImageTag.objects.filter(tag_name__in=tagslist).values_list(
            "image_id", flat=True
        )
        images = Image.objects.filter(user_id=userid, id__in=image_ids)
        urls = set(image.url for image in images)
        ids = set(image.id for image in images)

        # 计算所有标签的交集
        for tag_name in tagslist:
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
        userid = request.data.get("user_id")
        description = request.data.get("description")

        print("********************************************************")
        print(request.data)
        print("********************************************************")

        images = Image.objects.filter(user_id=userid)

        descriptionlist = [image.description for image in images]

        print(descriptionlist)

        similarityList = []
        for sentence in descriptionlist:
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
            {"image_id": image.id, "image_url": image.url}
            for image, _ in filtered_images
        ]

        idList = [item["image_id"] for item in result]
        urlList = [item["image_url"] for item in result]

        return JsonResponse(
            {"state": "success", "image_id": idList, "image_url": urlList}
        )


class SelectImages(APIView):
    def post(self, request, *args, **kwargs):
        userid = request.data.get("user_id")
        time = request.data.get("time")
        position = request.data.get("position")
        tags = request.data.get("tags")

        # 获取用户全部照片
        images = Image.objects.filter(user_id=userid)

        # 按时间筛选
        if time != "":
            images = images.filter(time=time)

        # 按地点筛选
        if position != "":
            images = images.filter(position=position)

        url1 = set(image.url for image in images)
        id1 = set(image.id for image in images)

        if len(tags) != 0:
            # 获取所有符合条件的图片的 URL 和 ID
            image_ids = ImageTag.objects.filter(tag_name__in=tags).values_list(
                "image_id", flat=True
            )
            images = Image.objects.filter(user_id=userid, id__in=image_ids)
            urls = set(image.url for image in images)
            ids = set(image.id for image in images)

            # 计算所有标签的交集
            for tag_name in tags:
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
            urlList = list(urls & url1)
            idList = list(ids & id1)

        else:
            urlList = list(url1)
            idList = list(id1)

        return JsonResponse(
            {"state": "success", "image_id": idList, "image_url": urlList}
        )
