from django.urls import path, include
from rest_framework import routers

from mimi_server.apps.meeting.views import RoomViewSet, OwnsRoomViewSet, RoomParticipatedUserViewSet

router = routers.DefaultRouter()
router.register(r'roomList', RoomViewSet, basename='room')
router.register(r'ownsRoomList', OwnsRoomViewSet, basename='ownsRoom')
router.register(r'userinfo', RoomParticipatedUserViewSet, basename='userinfo')

urlpatterns = [
    path('', include(router.urls)),
    # path('myRoomList/<int::id>', MyRoomViewSet)
]