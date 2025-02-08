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
