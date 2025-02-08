from apps.images.models import Image


def select_by_userid(user_id):
    images = Image.objects.filter(user_id=user_id)
    return images
