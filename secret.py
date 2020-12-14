import os
# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django_postgres_delete_cascade',
        'NAME': 'mimi',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

ALLOWED_HOSTS = ["*"]

EMAIL = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_USE_TLS': True,
    'EMAIL_PORT': 587,
    'EMAIL_HOST': 'smtp.gmail.com',
    'EMAIL_HOST_USER': os.environ["GMAIL_ID"],
    'EMAIL_HOST_PASSWORD': os.environ["GMAIL_PW"],
    'SERVER_EMAIL': os.environ["GMAIL_ID"].split("@")[0],
}

FIREBASE_SERVER_KEY = 'key=firebase_server_key'
KAKAO_REST_API_KEY = 'kakao_rest_api_key'
GOOGLE_APPLICATION_CREDENTIALS = 'service-account-file.json'
