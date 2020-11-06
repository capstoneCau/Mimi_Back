from django.urls import path, include
from rest_framework import routers

from mimi_server.apps.meeting.views import InviteeParcitipateRequestViewSet, InviteeCreateRequestViewSet, \
    InviterParticipateRequestViewSet, InviterCreateRequestViewSet, RequestUserViewSet, RequestRoomViewSet, \
        RequestCheckingView, SelectedRequestMatchingView

router = routers.DefaultRouter()
router.register('inviter/create', InviterCreateRequestViewSet, basename='inviter_create')
router.register('inviter/participate', InviterParticipateRequestViewSet, basename='inviter_participate')

router.register('invitee/create', InviteeCreateRequestViewSet, basename='invitee_create')
router.register('invitee/participate', InviteeParcitipateRequestViewSet, basename='invitee_participate')

router.register('userinfo', RequestUserViewSet, basename='request_userinfo')
router.register('roominfo', RequestRoomViewSet, basename='request_roominfo')

router.register('checking', RequestCheckingView, basename='request_checking')
router.register('select', SelectedRequestMatchingView, basename='request_select')

urlpatterns = [
    path('', include(router.urls)),
    # path('myRoomList/<int::id>', MyRoomViewSet)
]