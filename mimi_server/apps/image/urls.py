from django.conf import settings
from django.conf.urls.static import static
from mimi_server.apps.image.views import upload_file
from django.urls import path

urlpatterns = [
    path('', upload_file, name = 'image'),
]