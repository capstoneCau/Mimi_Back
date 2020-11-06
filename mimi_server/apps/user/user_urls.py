from django.urls import path, include
from rest_framework import routers
from .views import FriendsViewSet, SearchUserView

router = routers.DefaultRouter()

router.register(r'friends', FriendsViewSet, basename="friends")
router.register('search', SearchUserView, basename="search")
urlpatterns = [
    path('', include(router.urls)),
]