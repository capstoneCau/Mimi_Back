from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Room, Meeting
from ..user.models import FriendsParticipation
from ..user.models import User
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import api_view
from django.utils.datastructures import MultiValueDictKeyError

from .serializer import RoomSerializer, MeetingSerializer, RoomMeetingSerializer, \
    FriendsParticipationSerializer, ParticipationRoomUserSerializer

class AllRoomViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = RoomSerializer
    # permission_classes = (IsAuthenticated, )
    

    def get_queryset(self):
        lookup_field = 'id'
        # queryset = Room.objects.filter(status='a')
        queryset = Room.objects.all() #test
        return queryset

    def create(self, request, *args, **kwargs):
        # print(self.request.user, request.user)
        init_users = request.data.pop('init_users')
        request_user_id =  request.data.pop('request_user_id')

        createdRoom = Room.objects.create(**request.data)
        from_user = User.objects.filter(Q(kakao_auth_id=request_user_id)).first()
        keys = list(request.data.keys())
        for key in keys :
            request.data.pop(key)

        for user_id in init_users:
            request.data.update({
                "room" : createdRoom,
                "from_user" : from_user,
                "to_user" : User.objects.filter(Q(kakao_auth_id=user_id)).first(),
                "type" : "c",
            })
            FriendsParticipation.objects.create(**request.data)
        
        return createdRoom

class MyRoomViewSet(viewsets.ReadOnlyModelViewSet) :
    queryset = Meeting.objects.select_related('room')
    serializer_class = RoomMeetingSerializer

    def get_queryset(self):
        try:
            user_id, room_id = self.request.data['user_id'], self.request.data['room_id']
            queryset = Meeting.objects.select_related('room').filter(Q(user=user_id) & Q(room=room_id))
            print(queryset)
            return queryset
        except (MultiValueDictKeyError, KeyError) :
            return Meeting.objects.select_related('room')
    
    # def update(self, request, *args, **kwargs):
    #     user_id, room_id = kwargs["pk"].split(":")
    #     print(user_id, room_id)
    #     partial = kwargs.pop('partial', False)
    #     instance = Meeting.objects.select_related('room').filter(Q(user=user_id) & Q(room=room_id)).first()
        
    #     serializer = MeetingSerializer(instance, data=request.data, partial=partial)
        # serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)

        # if getattr(instance, '_prefetched_objects_cache', None):
        #     # If 'prefetch_related' has been applied to a queryset, we need to
        #     # forcibly invalidate the prefetch cache on the instance.
        #     instance._prefetched_objects_cache = {}

        # return Response(serializer.data)
        return Response(status=status.HTTP_200_OK)
    

class MeetingCreateRequestViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ParticipationRoomUserSerializer

    def get_queryset(self):
        try:
            from_user_id, to_user_id, room_id, _type = self.request.data['from_user_id'], self.request.data['to_user_id'], \
                self.request.data['room_id'], self.request.data['type']
            print(from_user_id, to_user_id, room_id, _type)
            queryset = FriendsParticipation.objects.select_related('room', 'from_user').filter(Q(type=_type))
            return queryset
        except (MultiValueDictKeyError, KeyError) :
            return FriendsParticipation.objects.select_related('room', 'from_user')

    def create(self, request, *args, **kwargs):
        participation_user_list = request.data.pop('participation_user_list')
        if len(set(participation_user_list)) != len(participation_user_list) :
            return Response({"detail" : "Duplicate users have been added.", "error" : "404"}, status=status.HTTP_400_BAD_REQUEST)
        request.data.update({
            "from_user" : User.objects.filter(Q(kakao_auth_id=request.data["from_user"])).first(),
            "room" : Room.objects.filter(Q(id=request.data["room"])).first()
        })
        instanceList = []
        if len(participation_user_list) > request.data["room"].user_limit:
            return Response({"detail": "You have exceeded the room limit.", "error" : "400"}, status=status.HTTP_400_BAD_REQUEST)
        for user_id in participation_user_list :
            if request.data["from_user"] == user_id:
                return Response({"detail":"The invited user and the invited user are the same.",
                "error" : "400"}, status=status.HTTP_400_BAD_REQUEST)
            instance = User.objects.filter(Q(kakao_auth_id=user_id)).first()
            if(instance == None) :
                return Response({"detail" : "This user does not exist.", "error" : "400"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                instanceList.append(instance)
        
        for instance in instanceList:
            request.data.update({
                'to_user' : instance
            })
            FriendsParticipation.objects.create(**request.data)

        return Response({"result" : True}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        room_id, from_user_id, to_user_id = kwargs["pk"].split(":")
        if Room.objects.filter(Q(id=room_id)).first().status == 'c' :
            return Response({"detail" : "The requested room has been cancelled.", "error" : 406}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if request.data["is_accepted"] not in ['a', 'r'] :
            return Response({"detail" : "Invalid input. is_accepted can only be'a' or 'r'.", "error" : 400, status=status.HTTP_400_BAD_REQUEST)
        
        if request.data["is_accepted"] == None :
            print(request.data)
            return Response({"detail" : "is_accepted does not exist.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(request.data) > 1 :
            return Response({"detail" : "Too many parameters.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

        partial = kwargs.pop('partial', False)
        instance = FriendsParticipation.objects.select_related('room', 'from_user', 'to_user').filter(Q(from_user_id=from_user_id) & Q(room=room_id) & Q(to_user_id=to_user_id)).first()
        
        serializer = FriendsParticipationSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        room = room = Room.objects.filter(Q(id=room_id))
        if request.data["is_accepted"] == 'r' :
            updatedData = {
                "status" : 'c'
            }
            room.update(**updatedData)
            return Response(RoomSerializer(room.first()).data, status=status.HTTP_205_RESET_CONTENT)

        allRequestList = FriendsParticipation.objects.filter(Q(room=room_id))
        isAllAccept = True
        for e in allRequestList:
            isAllAccept &= (e.is_accepted == 'a')

        if isAllAccept : 
            updatedData = {
                'status' : 'a'
            }
            room.update(**updatedData)
            room = room.first()
            for e in allRequestList:
                user = User.objects.filter(Q(kakao_auth_id=e.to_user)).first()
                meetingInfo = {
                    "room" : room,
                    "user" : user,
                    "type" : e.type,
                    "user_role" : 'g'
                }
                Meeting.objects.create(**meetingInfo)
            user = User.objects.filter(Q(kakao_auth_id=e.from_user)).first()
            meetingInfo = {
                "room" : room,
                "user" : user,
                "type" : e.type,
                "user_role" : 'a' if e.type == 'c' else 'g'
            }
            Meeting.objects.create(**meetingInfo)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        room_id, from_user_id, to_user_id = kwargs["pk"].split(":")
        instance = instance = FriendsParticipation.objects.select_related('room', 'from_user', 'to_user').filter(Q(from_user_id=from_user_id) & Q(room=room_id) & Q(to_user_id=to_user_id)).first()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
        


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
