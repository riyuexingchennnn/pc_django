from apps.images.models import Image, ImageTag


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
