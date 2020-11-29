from django.conf import settings
from django.conf.urls.static import static
from mimi_server.apps.image.views import detect_face, get_animal_image
from django.urls import path

urlpatterns = [
    path('detect', detect_face, name='detect_face'),
    path('getImage', get_animal_image, name='get_animal')
]
