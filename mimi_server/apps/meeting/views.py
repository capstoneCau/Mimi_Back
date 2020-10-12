from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Room, Meeting
from ..user.models import FriendsParticipation
from ..user.models import User
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import api_view
from django.utils.datastructures import MultiValueDictKeyError

from .serializer import RoomSerializer, MeetingSerializer, RoomMeetingSerializer, FriendsParticipationSerializer, ParticipationRoomSerializer

class AllRoomViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RoomSerializer
    # permission_classes = (IsAuthenticated, )
    

    def get_queryset(self):
        lookup_field = 'id'
        # queryset = Room.objects.filter(status='a')
        queryset = Room.objects.all() #test
        return queryset

class MyRoomViewSet(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet) :
    queryset = Meeting.objects.select_related('room')
    serializer_class = RoomMeetingSerializer
    lookup_field = 'user'

    def update(self, request, user, *args, **kwargs):
        # room_id = request.data.pop('room_id')
        # is_active = request.data.pop('is_active')
        # queryset = Meeting.objects.filter(Q(room=room_id) & Q(user=user))
        print(request.data.get('room').pop('id'))
        print(request.data)

        return Response(status=status.HTTP_200_OK)
    # def create(self, request, *args, **kwargs):
    #     # print(self.request.user, request.user)
    #     init_users = request.data.get('init_users')
    #     request_user_id = request.data.get('request_user_id')

    #     request.data.pop('init_users')
    #     request.data.pop('request_user_id')
        
    #     createdRoom = Room.objects.create(**request.data)
    #     keys = list(request.data.keys())
    #     for key in keys :
    #         request.data.pop(key)

    #     for user_id in init_users:
    #         request.data.update({
    #             "room_id" : createdRoom,
    #             "user_id" : User.objects.filter(Q(kakao_auth_id=user_id)).first(),
    #             "user_role" : "a" if user_id == request_user_id else "g",
    #             "type" : "c"
    #         })
    #         Meeting.objects.create(**request.data)
        
    #     return createdRoom

class MeetingCreateRequestViewSet(viewsets.ViewSet):
    serializer_class = ParticipationRoomSerializer

    def get_queryset(self):
        queryset = FriendsParticipation.objects.select_related('room').filter(Q(from_user=self.request.data["user_id"]) & Q(type='c') & Q(is_accepted='w'))
        return queryset

    def create(self, request, *args, **kwargs):
        participation_user_list = request.data.get('participation_user_list')
        request.data.pop('participation_user_list')
        instanceList = []
        for user_id in participation_user_list :
            instance = User.objects.filter(Q(user_id=user_id))
            if(instance == None) :
                return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                instanceList.append(instance)
        
        for instance in instanceList:
            request.data.update({
                'to_user' : instance
            })
            FriendsParticipation.objects.create(**request.data)

        return Response(status=status.HTTP_201_CREATED)
    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     if request.user == instance.user_id:
    #         self.perform_destroy(instance)
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     else:
    #         return Response(status=status.HTTP_401_UNAUTHORIZED)


# class ListMeetingRequestViewSet(viewsets.ModelViewSet):
#     serializer_class = MeetingInfoSerializer

#     def get_queryset(self):
#         my_meeting_id = get_my_meeting_id(self.request.user)
#         is_active = self.request.GET.get('is_active', True)  # active : 요청 한(true) / 요청 받은(false)
#         queryset = []

#         if is_active == 'True':
#             requested_list = MeetingRequest.objects.filter(requestor_meeting_id=my_meeting_id)
#         else:
#             requested_list = MeetingRequest.objects.filter(author_meeting_id=my_meeting_id)

#         for requested in requested_list:
#             if is_active == 'True':
#                 meeting = MeetingInfo.objects.get(Q(id=requested.author_meeting_id) & Q(status='activate'))
#             else:
#                 meeting = MeetingInfo.objects.get(Q(id=requested.requestor_meeting_id) & Q(status='activate'))
#             if meeting is not None:
#                 queryset.insert(0, meeting)

#         set_am_i_requested_field(queryset, my_meeting_id)
#         return queryset


# class MeetingRequestViewSet(viewsets.ModelViewSet):
#     serializer_class = MeetingRequestSerializer
#     queryset = MeetingRequest.objects.all()

#     def create(self, request, *args, **kwargs):
#         author = request.data.get('author_meeting_id')
#         requestor = get_my_meeting_id(request.user)
#         request.data['requestor_meeting_id'] = requestor

#         # check 409
#         requested_meeting = MeetingRequest.objects.all()
#         if requested_meeting.filter(Q(author_meeting_id=author) & Q(requestor_meeting_id=requestor)).exists():
#             return Response(status=status.HTTP_409_CONFLICT)

#         # check 404
#         author_meeting = MeetingInfo.objects.filter(Q(status='activate') & Q(id=author))
#         requestor_meeting = MeetingInfo.objects.filter(Q(status='activate') & Q(id=requestor))
#         if not author_meeting.exists() or not requestor_meeting.exists():
#             return Response(status=status.HTTP_404_NOT_FOUND)

#         return super().create(request, *args, **kwargs)


# class ListMeetingMatchedViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = MeetingInfoSerializer

#     def get_queryset(self):
#         my_meeting_id = get_my_meeting_id(self.request.user)
#         try:
#             id_list = MeetingMatchedId.objects.get(
#                 Q(author_meeting_id=my_meeting_id) | Q(requestor_meeting_id=my_meeting_id))
#             queryset = MeetingInfo.objects.filter(Q(id=id_list.author_meeting_id) | Q(id=id_list.requestor_meeting_id))
#         except MeetingMatchedId.DoesNotExist:
#             queryset = []

#         set_am_i_requested_field(queryset, my_meeting_id)
#         return queryset


# class MeetingMatchedViewSet(viewsets.ModelViewSet):
#     serializer_class = MeetingMatchedSerializer
#     queryset = MeetingMatched.objects.all()

#     def create(self, request, *args, **kwargs):
#         requestor_meeting_id = request.data.get('requestor_meeting_integer_id')
#         author_meeting = MeetingInfo.objects.filter(Q(status='activate') & Q(author=request.user)).first()
#         requestor_meeting = MeetingInfo.objects.filter(Q(status='activate') & Q(id=requestor_meeting_id)).first()

#         # check 404
#         if not author_meeting or not requestor_meeting:
#             return Response(status=status.HTTP_404_NOT_FOUND)

#         # check 404
#         if not MeetingRequest.objects.filter(
#                 Q(author_meeting_id=author_meeting.id) & Q(requestor_meeting_id=requestor_meeting_id)).exists():
#             return Response(status=status.HTTP_403_FORBIDDEN)

#         # check 409
#         matched_meeting = MeetingMatched.objects.all()
#         if matched_meeting.filter(Q(author_meeting=author_meeting) & Q(requestor_meeting=requestor_meeting)).exists():
#             return Response(status=status.HTTP_409_CONFLICT)
#         if matched_meeting.filter(Q(author_meeting=requestor_meeting) & Q(requestor_meeting=author_meeting)).exists():
#             return Response(status=status.HTTP_409_CONFLICT)

#         return super().create(request, *args, **kwargs)
