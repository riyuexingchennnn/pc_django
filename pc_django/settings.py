"""
Django settings for pc_django project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
    
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-t2b+ayog=i2hk)&9*c@ey=$=r5fzn_4dh$7#l%97x@+q-o-ae_"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "rcsvnfd47bsc.ngrok.xiaomiqiu123.top",  # 你的外部域名
    "http://rcsvnfd47bsc.ngrok.xiaomiqiu123.top",  # 如果是 HTTP 协议也需要添加
    "https://rcsvnfd47bsc.ngrok.xiaomiqiu123.top",
    "localhost",  # 本地地址
    "127.0.0.1",  # 本地地址
    "192.168.134.35",  # 局域网地址
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",  # 跨域请求
    # ----------- 自定义应用 -----------
    "apps.accounts",
    "apps.ai",
    "apps.images",
    "apps.pay",
    "apps.search",
    "apps.qr_code",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # 跨域请求
    "apps.utils.middleware.LoginInterceptorMiddleware",  # 登录拦截器
]

# 允许所有来源访问
CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = "pc_django.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "pc_django.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

import pymysql

pymysql.install_as_MySQLdb()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "piccloud",  # 这里是你创建的数据库名
        "USER": "root",  # 这里是你创建的数据库用户名
        "PASSWORD": "1234",  # 这里是你设置的密码，windows上必须4位，呜呜呜
        "HOST": "localhost",
        "PORT": "3306",  # 默认端口
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "zh-Hans"

TIME_ZONE = "Asia/Shanghai" # 设为你所在的时区

USE_I18N = False

USE_TZ = True # 开启时区支持


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --------------------- 媒体文件配置 ------------------------
import os

# 设置媒体文件的存储位置
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# 设置媒体文件的URL
MEDIA_URL = "/media/"

# --------------------- 日志配置 ----------------------------
from datetime import datetime

USE_RELOADER = False

# 获取当前时间，格式化为日志文件名
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 日志文件夹路径
LOG_DIR = os.path.join(BASE_DIR, "log")

# 如果日志文件夹不存在，自动创建
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",  # 只记录 DEBUG 级别及以上的日志
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "INFO",  # 记录 INFO 级别及以上的日志
            "class": "logging.FileHandler",
            "filename": os.path.join(
                LOG_DIR, f"django_{current_time}.log"
            ),  # 文件名以时间为后缀
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],  # 输出到控制台和文件
            "level": "DEBUG",
            "propagate": False,  # 关闭向父级传递日志
        },
        "django.utils.autoreload": {
            "handlers": ["file"],  # 只输出到文件
            "level": "ERROR",  # 将 autoreload 模块的日志级别设置为 ERROR
            "propagate": False,  # 禁止自动传播 autoreload 的日志
        },
    },
}
# --------------------------------------------------------------------
