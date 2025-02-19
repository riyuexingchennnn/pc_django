from django.http import JsonResponse
from rest_framework.views import APIView
from apps.utils.token_util import parse_token
from apps.images.models import Image, ImageTag
from apps.search.utils.Select_methods import (
    select_by_userid,
    select_by_time,
    select_by_position,
    select_by_tags,
    select_by_description,
    select_by_timezone,
)
from apps.images.models import ImageTag
from .utils.citydata import data_
from ..utils.token_util import parse_token


# lc
# 使用组合索引+覆盖索引优化查询过程
# 优化过程与范围时间搜索相同

class SelectImagesByTime(APIView):
    # 按时间搜索,格式：2025-08-20
    def post(self, request, *args, **kwargs):
        # 识别搜素模式（按时间搜索）
        token = request.META.get("HTTP_AUTHORIZATION")
        payload = parse_token(token)
        user_id = payload.get("user_id")
        # user_id = request.data.get("user_id")
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
# lc
# 优化过程：去除重复遍历，使用组合索引+覆盖索引优化查询过程
# SQL：CREATE INDEX combined_index ON Image (user_id, time)
# SQL：select id, url from images where user_id = 'user_id' and time >= 'start_time' and time <= 'end_time'
# class SelectImagesByTimeZone(APIView):
#     def post(self, request, *args, **kwargs):
#         token = request.META.get("HTTP_AUTHORIZATION")
#         payload = parse_token(token)
#         user_id = payload.get("user_id")
#         start_time = request.data.get("starttime")
#         end_time = request.data.get("endtime")
        
#         queryset = Image.objects.filter(
#             user_id = user_id,
#             time__gte = start_time,
#             time__lte = end_time
#         ).only('id', 'url')
#         # 将QuerySet转换为包含id和url的字典列表
#         result = list(queryset.values('id', 'url'))
#         return result


class SelectImagesByTimeZone(APIView):
    def post(self, request, *args, **kwargs):
        token = request.META.get("HTTP_AUTHORIZATION")
        payload = parse_token(token)
        user_id = payload.get("user_id")
        # user_id = request.data.get("user_id")
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
# lc
# 由于左模糊搜索无法使用索引，除了要全表扫描，并且要挨个进行字符串匹配
# 所以阿里巴巴java开发手册中是禁用左模糊搜索的
# 除此之外，将国家省份市区存储在一个字段中是违反数据库第一范式的



class SelectImagesByPosition(APIView):
    # 按地点搜索
    def post(self, request, *args, **kwargs):
        token = request.META.get("HTTP_AUTHORIZATION")
        payload = parse_token(token)
        user_id = payload.get("user_id")
        # user_id = request.data.get("user_id")
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

# lc
# 使用子查询与分组查询优化多次筛选过程
# SQL:select image_id,image_url where image_id in (select image_id from tag where tag_name in (tag_list) group by image_id having count(tag_name) = len(tags_list))
#def get_images(tag_list):
#    subquery = Tag.objects.filter(tag_name__in=tag_list).values('image_id').annotate(tag_count=models.Count('tag_name')).filter(tag_count=len(tag_list)).values('image_id')
#    images = Image.objects.filter(image_id__in=subquery).only('image_id', 'image_url')
#    return list(images.values('image_id', 'image_url'))
class SelectImagesByTags(APIView):
    # 按照标签搜索图片
    def post(self, request, *args, **kwargs):
        token = request.META.get("HTTP_AUTHORIZATION")
        payload = parse_token(token)
        user_id = payload.get("user_id")
        # user_id = request.data.get("user_id")
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
        token = request.META.get("HTTP_AUTHORIZATION")
        payload = parse_token(token)
        user_id = payload.get("user_id")
        # user_id = request.data.get("user_id")
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
        token = request.META.get("HTTP_AUTHORIZATION")
        payload = parse_token(token)
        user_id = payload.get("user_id")
        # user_id = request.data.get("user_id")
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


class GetTags(APIView):
    def post(self, request, *args, **kwargs):
        token = request.META.get("HTTP_AUTHORIZATION")
        payload = parse_token(token)
        user_id = payload.get("user_id")
        # user_id = request.data.get("user_id")
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


class GetProvinces(APIView):
    def get(self, *args, **kwargs):
        provinces = [province["name"] for province in data_["districts"]]
        return JsonResponse({"provinces": provinces})


class GetCity(APIView):
    def post(self, request, *args, **kwargs):
        province = request.data_.get("province")
        for prov in data_["districts"]:
            if prov["name"] == province:
                cities = [city["name"] for city in prov["districts"]]
                return JsonResponse({"cities": cities})


class GetDistrict(APIView):
    def post(self, request, *args, **kwargs):
        city = request.data.get("city")
        for prov in data_["districts"]:
            for cy in prov["districts"]:
                if cy["name"] == city:
                    districts = [district["name"] for district in cy["districts"]]
                    return JsonResponse({"districts": districts})
