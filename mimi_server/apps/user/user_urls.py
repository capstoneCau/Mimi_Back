from django.urls import path, include
from rest_framework import routers
from .views import FriendsViewSet, SearchUserView, FcmTokenView

router = routers.DefaultRouter()

router.register(r'friends', FriendsViewSet, basename="friends")
router.register('search', SearchUserView, basename="search")
router.register('fcmToken', FcmTokenView, basename='fcmtoken')
urlpatterns = [
    path('', include(router.urls)),
]