from django.contrib import admin
from .models import User

from apps.images.models import Image, ImageTag
admin.site.register(User)

