"""
Django settings for messenger project.
"""

from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

APPEND_SLASH = False

ALLOWED_HOSTS = ['*']

SECRET_KEY = "django-insecure-5)2bq*7$vs9zy8+wfao(x@8#_si6a@bxtu&e%@n#r@wv@%tdp4"
DEBUG = True


# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'corsheaders',
    'channels',
    
    # Your apps
    'users',
    'servers',
    'chatting',
    
]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'users.middleware.UpdateLastSeenMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.joinpath('templates/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = 'config.asgi.application'


# ==================== DATABASE ====================
 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ==================== PASSWORD VALIDATION ====================
 
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ==================== INTERNATIONALIZATION ====================
 
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ==================== STATIC FILES & MEDIA ====================
 
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
 
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
 
# ==================== DEFAULT PRIMARY KEY ====================
 
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
 
# ==================== CUSTOM USER MODEL ====================
 
AUTH_USER_MODEL = 'users.User'
 
# ==================== REST FRAMEWORK ====================
 
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',  # Session-based auth
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}
 
# ==================== CSRF SECURITY ====================
 
# 🔒 Cookie security зависит от режима (dev/prod)
CSRF_COOKIE_SECURE = not DEBUG      # True в production (HTTPS only)
CSRF_COOKIE_HTTPONLY = False        # False — фронтенду нужно читать CSRF токен
CSRF_COOKIE_AGE = 31449600          # 1 год
 
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:5173,http://127.0.0.1:5173'
).split(',') # type: ignore
 
# ==================== SESSION SECURITY ====================
 
# 🔒 Session security зависит от режима (dev/prod)
SESSION_COOKIE_SECURE = not DEBUG   # True в production (HTTPS only)
SESSION_COOKIE_HTTPONLY = True      # Защита от XSS (только HTTP, не JavaScript)
SESSION_COOKIE_AGE = 1209600        # 2 недели
SESSION_COOKIE_SAMESITE = 'Lax'     # Защита от CSRF (Lax/Strict)
 
# ==================== CORS SECURITY ====================
 
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:5173,http://127.0.0.1:5173'
).split(',') # type: ignore
 
CORS_ALLOW_CREDENTIALS = True  # Разрешить cookies в cross-origin запросах
 
# ==================== REDIS CACHE ====================
# 🔒 Используется для кеширования данных (servers, users)
# DB 1 — для кеша
# DB 0 — для Channels (WebSocket)
# DB 2 — для Celery (если используется)
 
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,  # Продолжить работу если Redis упал
        },
        'KEY_PREFIX': 'flex_messenger',
        'TIMEOUT': 300,  # Дефолтный timeout 5 минут
    }
}
 

 
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
 
# ==================== EMAIL CONFIGURATION ====================
# 🔒 SMTP credentials должны быть в .env файле

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ==================== CELERY CONFIGURATION ====================
# 🔒 Настройки для асинхронных задач

CELERY_BROKER_URL = config('REDIS_URL', default='redis://127.0.0.1:6379/2')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://127.0.0.1:6379/2')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Настройки beat для периодических задач
from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'delete-expired-unverified-users': {
        'task': 'users.tasks.delete_expired_unverified_users',
        'schedule': crontab(minute='*/10'),  # Каждые 10 минут
    },
}
 
# ==================== LOGGING CONFIGURATION ====================
# 🔒 Логирование в консоль (dev) и в файл (prod)
 
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {funcName}:{lineno} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s[%(levelname)s]%(reset)s %(asctime)s %(name)s %(funcName)s:%(lineno)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'log_colors': {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            'force_color': True,
        },
        'simple': {
            'format': '[{levelname}] {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG' if DEBUG else 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'users': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'servers': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'chatting': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
 