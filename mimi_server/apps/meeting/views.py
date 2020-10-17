from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Room, Meeting, FriendsParticipation
from ..user.models import User
from ..user.serializer import UserSerializer
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import api_view
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly

from .serializer import RoomSerializer, MeetingRoomSerializer, MeetingUserSerializer, ParticipationRoomUserSerializer, \
    ParticipatiedUserSerializer, ParticipatiedRoomSerializer

class RoomViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = RoomSerializer
    
    def get_queryset(self):
        try:
            id = self.kwargs['pk']
            queryset = Room.objects.filter(Q(id=id)) #test
            return queryset
        except KeyError:
            queryset = Room.objects.exclude(meeting=self.request.user).filter(status='a').all() #test
            # queryset = Room.objects.all() #test
            # print(queryset.query)
            return queryset

    def create(self, request, *args, **kwargs):
        init_users = request.data.pop('init_users')
        if request.user in init_users :
            return Response({"detail" : "The room creator has been invited.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

        if request.data["user_limit"] > len(init_users)+1 :
            return Response({"detail" : 'The number of participants in the meeting is small. Input user_limit : ' + str(request.data["user_limit"]) + ' Init user number(Include you) : ' + str(len(init_users)+1), "error" : 400}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.data["user_limit"] < len(init_users)+1 :
            return Response({"detail" : 'The number of participants in the meeting is large. Input user_limit : ' + str(request.data["user_limit"]) + ' Init user number(Include you) : ' + str(len(init_users)+1), "error" : 400}, status=status.HTTP_400_BAD_REQUEST)
            
        createdRoom = Room.objects.create(**request.data)
        
        inviter = User.objects.filter(Q(kakao_auth_id=request.user)).first()

        for user_id in init_users:
            createdData = {
                "room" : createdRoom,
                "user" : User.objects.filter(Q(kakao_auth_id=user_id)).first(),
                "type" : "c",
                "user_role" : "invitee"
            }
            FriendsParticipation.objects.create(**createdData)
        
        createdData = {
                "room" : createdRoom,
                "user" : inviter,
                "type" : "c",
                "is_accepted" : "a",
                "user_role" : "inviter"
        }
        FriendsParticipation.objects.create(**createdData)

        return Response(RoomSerializer(createdRoom).data, status=status.HTTP_200_OK)

class OwnsRoomViewSet(viewsets.ReadOnlyModelViewSet) :
    serializer_class = MeetingRoomSerializer

    def get_queryset(self):
        try:
            user = self.request.data['user']
            return Meeting.objects.select_related('room').filter(Q(user=user))
        except KeyError:
            queryset = Meeting.objects.select_related('room').filter(Q(user=self.request.user))
            print(queryset.query)
            return queryset
            

class RoomParticipatedUserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MeetingUserSerializer

    def get_queryset(self):
        try:
            room = self.request.data['room']
            queryset = Meeting.objects.select_related('user').filter(Q(room=room))
            print(queryset.all())
            return queryset.all()
        except KeyError :
            return None

class RequestUserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ParticipatiedUserSerializer

    def get_queryset(self):
        try:
            request_id = self.request.data['request']
            request = FriendsParticipation.objects.filter(Q(id=request_id)).first()
            room_id = request.room.id
            queryset = FriendsParticipation.objects.select_related('user').filter(Q(room=room_id) & ~Q(user=self.request.user))
            return queryset
        except KeyError :
            return None

class RequestRoomViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ParticipatiedRoomSerializer

    def get_queryset(self):
        try:
            id = self.kwargs['pk']
            queryset = FriendsParticipation.objects.select_related('room').filter(Q(id=id))
            return queryset
        except KeyError :
            return None
    

class InviteeParcitipateRequestViewSet(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet) :
    serializer_class = ParticipationRoomUserSerializer
    def get_queryset(self):
        try:
            id = self.kwargs['pk']
            queryset = FriendsParticipation.objects.select_related('room', 'user').filter(Q(id=id))
            return queryset
        except (MultiValueDictKeyError, KeyError) :
            return FriendsParticipation.objects.select_related('room', 'user').filter(user=self.request.user, type='p', user_role='invitee').exclude(room__status='c')

    def update(self, request, *args, **kwargs):
        instance = FriendsParticipation.objects.filter(Q(id=kwargs['pk'])).first()
        room = Room.objects.filter(Q(id=instance.room.id))

        if instance.user.kakao_auth_id != str(request.user) :
            return Response({"detail": "User Id is different.", "error" : 401}, status=status.HTTP_401_UNAUTHORIZED)

        if instance.user_role != 'invitee' :
            return Response({"detail": "User is inviter.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

        if instance.type != 'p' :
            return Response({"detail" : "Request ID type is not 'p'.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

        if instance.is_accepted != 'w' :
            return Response({"detail" : "You have already responded, or someone on your team has declined.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

        if room.first().status == 'c' :
            return Response({"detail" : "The requested room has been cancelled.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

        if room.first().status == 'm' :
            return Response({"detail" : "The requested room has been matched.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

        if request.data["is_accepted"] == None: 
            return Response({"detail" : "Add the 'is_accepted' data.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.data["is_accepted"] not in ['a', 'r'] :
            return Response({"detail" : "Invalid input. is_accepted can only be'a' or 'r'.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

        if len(request.data) >= 2 : 
            return Response({"detail" : "Add data only to 'is_accepted'.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

        partial = kwargs.pop('partial', False)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        
        allRequestList = FriendsParticipation.objects.filter(Q(room=instance.room.id) & Q(type='p'))

        if request.data["is_accepted"] == 'r' :
            for e in allRequestList:
                updatedData = {
                    "is_accepted" : 'r'
                }
                e.update(**updatedData)
            return Response(RoomSerializer(room.first()).data, status=status.HTTP_205_RESET_CONTENT)

        
        isAllAccept = True
        for e in allRequestList:
            isAllAccept &= (e.is_accepted == 'a')

        if isAllAccept : 
            updatedData = {
                'status' : 'm'
            }
            room.update(**updatedData)
            room = room.first()
            for e in allRequestList:
                user = User.objects.filter(Q(kakao_auth_id=e.user.kakao_auth_id)).first()
                meetingInfo = {
                    "room" : room,
                    "user" : user,
                    "type" : e.type,
                    "user_role" : 'g'
                }
                Meeting.objects.create(**meetingInfo)

        return Response(serializer.data, status=status.HTTP_200_OK)

class InviteeCreateRequestViewSet(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet) :
    serializer_class = ParticipationRoomUserSerializer
    def get_queryset(self):
        try:
            id = self.kwargs['pk']
            queryset = FriendsParticipation.objects.select_related('room', 'user').filter(Q(id=id))
            return queryset
        except (MultiValueDictKeyError, KeyError) :
            queryset = FriendsParticipation.objects.select_related('room', 'user').filter(user=self.request.user, type='c', user_role='invitee').exclude(room__status='c')
            return queryset

    def update(self, request, *args, **kwargs):
        try:
            instance = FriendsParticipation.objects.filter(Q(id=kwargs['pk'])).first()
            # print(instance.invitee.kakao_auth_id+"||"+str(request.user)+"||")
            if instance.user.kakao_auth_id != str(request.user) :
                return Response({"detail": "User Id is different.", "error" : 401}, status=status.HTTP_401_UNAUTHORIZED)

            if instance.user_role != 'invitee' :
                return Response({"detail": "User is inviter.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

            if instance.type != 'c' :
                return Response({"detail" : "Request ID type is not 'c'.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

            if Room.objects.filter(Q(id=instance.room.id)).first().status == 'c' :
                return Response({"detail" : "The requested room has been cancelled.", "error" : 406}, status=status.HTTP_400_BAD_REQUEST)

            if request.data["is_accepted"] == None: 
                return Response({"detail" : "Add the 'is_accepted' data.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)
            
            if request.data["is_accepted"] not in ['a', 'r'] :
                return Response({"detail" : "Invalid input. is_accepted can only be 'a' or 'r'.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

            if len(request.data) >= 2 : 
                return Response({"detail" : "Add data only to 'is_accepted'.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

            partial = kwargs.pop('partial', False)
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}
            
            room = Room.objects.filter(Q(id=instance.room.id))
            if request.data["is_accepted"] == 'r' :
                updatedData = {
                    "status" : 'c'
                }
                room.update(**updatedData)
                return Response(RoomSerializer(room.first()).data, status=status.HTTP_205_RESET_CONTENT)
            
            allRequestList = FriendsParticipation.objects.filter(Q(room=instance.room.id) & Q(type='c'))
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
                    user = User.objects.filter(Q(kakao_auth_id=e.user.kakao_auth_id)).first()
                    meetingInfo = {
                        "room" : room,
                        "user" : user,
                        "type" : e.type,
                        "user_role" : 'g' if e.user_role == 'invitee' else 'a'
                    }
                    Meeting.objects.create(**meetingInfo)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except KeyError :
            return Response({"detail" : "Invalid input.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

class InviterParticipateRequestViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ParticipationRoomUserSerializer

    def get_queryset(self):
        try:
            id = self.kwargs['pk']
            queryset = FriendsParticipation.objects.select_related('room', 'user').filter(Q(id=id))
            return queryset
        except (MultiValueDictKeyError, KeyError) :
            queryset = FriendsParticipation.objects.select_related('room', 'user').filter(user=self.request.user, type='p', user_role='inviter').exclude(room__status='c')
            print(queryset.query)
            return queryset

    def create(self, request, *args, **kwargs):
        participation_user_list = request.data.pop('participation_user_list')
        if len(set(participation_user_list)) != len(participation_user_list) :
            return Response({"detail" : "Duplicate users have been added.", "error" : "404"}, status=status.HTTP_400_BAD_REQUEST)

        request.data.update({
            "room" : Room.objects.filter(Q(id=request.data["room"])).first(),
            "type" : 'p'
        })
        
        instanceList = []
        if len(participation_user_list) > request.data["room"].user_limit:
            return Response({"detail": "You have exceeded the room limit.", "error" : "400"}, status=status.HTTP_400_BAD_REQUEST)

        for user_id in participation_user_list :
            if request.user == user_id:
                return Response({"detail":"The invited user and the invited user are the same.",
                "error" : "400"}, status=status.HTTP_400_BAD_REQUEST)
            instance = User.objects.filter(Q(kakao_auth_id=user_id)).first()
            if(instance == None) :
                return Response({"detail" : "This user does not exist.", "error" : "400"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                instanceList.append(instance)
        instanceList.append(User.objects.filter(Q(kakao_auth_id=request.user)).first())
        for instance in instanceList:
            request.data.update({
                'user' : instance,
                'is_accpeted' : 'w' if instance.kakao_auth_id != str(request.user) else 'a',
                'user_role' : 'invitee' if instance.kakao_auth_id != str(request.user) else 'inviter'
            })
            instance = FriendsParticipation.objects.create(**request.data)

        return Response(ParticipationRoomUserSerializer(instance).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        room, invitee_user = kwargs["pk"].split(":")
        instance = FriendsParticipation.objects.select_related('room', 'inviter_user', 'invitee_user').filter(Q(inviter_user=request.user) & Q(room=room) & Q(invitee_user=invitee_user)).first()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class InviterCreateRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ParticipationRoomUserSerializer

    def get_queryset(self):
        return FriendsParticipation.objects.select_related('room', 'user').filter(user=self.request.user, type='c', user_role='inviter').exclude(room__status='c')