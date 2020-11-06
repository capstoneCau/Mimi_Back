from django.urls import path, include
from rest_framework import routers
from .views import FriendsViewSet

router = routers.DefaultRouter()

router.register(r'friends', FriendsViewSet, basename="friends")

urlpatterns = [
    path('', include(router.urls)),
]