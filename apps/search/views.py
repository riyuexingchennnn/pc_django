from django.http import JsonResponse
from rest_framework.views import APIView
from apps.images.models import Image, ImageTag
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
        images_url = [image.url for image in images]
        images_id = [image.id for image in images]
        return JsonResponse(
            {
                "state": "success",
                "images_url": images_url,
                "images_id": images_id,
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
                "images_url": images_url,
                "images_id": images_id,
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

        urlList = []
        idList = []

        for tag_name in tagslist:
            image_ids = ImageTag.objects.filter(tag_name=tag_name).values_list(
                "image_id", flat=True
            )
            images = Image.objects.filter(user_id=userid, id__in=image_ids)
            urls = [image.url for image in images]
            ids = [image.id for image in images]

            if tag_name == tagslist[0]:
                urlList = urls
                idList = ids
            else:
                urlList = list(set(urlList) & set(urls))
                idList = list(set(idList) & set(ids))

        return JsonResponse(
            {
                "state": "success",
                "urls": urlList,
                "ids": idList,
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

        # 使用TF-IDF对描述进行向量化
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(descriptionlist + [description])

        # 计算每个图片描述与输入描述的余弦相似度
        similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])

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

        return JsonResponse({"state": "success", "images": result})
