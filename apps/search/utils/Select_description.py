from apps.search.utils.Cosine_similarity import cos_similarity


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
