from django.urls import path, include
from rest_framework import routers

from mimi_server.apps.meeting.models import Room, Meeting
from mimi_server.apps.user.models import FriendsParticipation
from mimi_server.apps.meeting.views import AllRoomViewSet, MeetingCreateRequestViewSet, \
    MyRoomViewSet, MeetingCreateRequestViewSet

router = routers.DefaultRouter()
router.register(r'allRoomList', AllRoomViewSet, basename='allRoom')
router.register('myRoomList', MyRoomViewSet, basename='myRoom')
router.register('meetingCreateRequestList', MeetingCreateRequestViewSet, basename='meetingCreateRequest')

urlpatterns = [
    path('', include(router.urls)),
    # path('myRoomList/<int::id>', MyRoomViewSet)
]