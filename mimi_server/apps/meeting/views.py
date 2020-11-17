from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Room, Meeting, FriendsParticipation
from mimi_server.apps.user.models import User
from mimi_server.apps.user.serializer import UserSerializer
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import api_view
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from django.db.models import Count

from .serializer import RoomSerializer, MeetingRoomSerializer, MeetingUserSerializer, ParticipationRoomUserSerializer, \
    ParticipatiedUserSerializer, ParticipatiedRoomSerializer, FriendsParticipationSerializer, SelectedParticipationSerializer

from ..notification.views import send
class RoomViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        try:
            room_id = self.request.GET['room']
            queryset = Room.objects.filter(Q(id=room_id)) #test
            return queryset
        except KeyError:
            queryset = Room.objects.exclude(Q(meeting__gender=self.request.user.gender)).filter(Q(status='a')).all()
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
        
        # inviter = User.objects.filter(Q(kakao_auth_id=request.user)).first()
        inviter = User.objects.get(Q(kakao_auth_id=request.user))
        inviteeFcmList = []
        for user_id in init_users:
            # invitee = User.objects.filter(Q(kakao_auth_id=user_id)).first()
            invitee = User.objects.get(Q(kakao_auth_id=user_id))
            createdData = {
                "room" : createdRoom,
                "user" : invitee,
                "type" : "c",
                "user_role" : "invitee",
                "party_number" : str(createdRoom.id) + inviter.kakao_auth_id
            }
            FriendsParticipation.objects.create(**createdData)
            inviteeFcmList.append(invitee.fcmToken)
        
        # send(inviteeFcmList, "미팅 생성 요청이 왔습니다.", inviter.name + "님께서 미팅 생성 요청을 보냈습니다.")

        createdData = {
                "room" : createdRoom,
                "user" : inviter,
                "type" : "c",
                "is_accepted" : "a",
                "user_role" : "inviter",
                "party_number" : str(createdRoom.id) + inviter.kakao_auth_id
        }
        FriendsParticipation.objects.create(**createdData)

        return Response(RoomSerializer(createdRoom).data, status=status.HTTP_200_OK)
    def destroy(self, request, *args, **kwargs):
        try:
            request = FriendsParticipation.objects.get(Q(room=kwargs['pk']) & Q(user=request.user))
        except FriendsParticipation.DoesNotExist:
            return Response({"detail":"The user does not belong to the room.", "error" : 404}, status=status.HTTP_404_NOT_FOUND)
        if request.user_role != 'inviter' or request.type != 'c':
            return Response({"detail":"The user is not a room manager.", "error" : 401}, status=status.HTTP_401_UNAUTHORIZED)
        instance = Room.objects.filter(Q(id=kwargs['pk'])).first()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

        
class OwnsRoomViewSet(viewsets.ReadOnlyModelViewSet) :
    serializer_class = MeetingRoomSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = Meeting.objects.select_related('room').filter(Q(user=self.request.user))
        return queryset
            
class RoomParticipatedUserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MeetingUserSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        try:
            room = self.request.GET['room']
            queryset = Meeting.objects.select_related('user').filter(Q(room=room)).exclude(Q(user=self.request.user))
            return queryset.all()
        except KeyError :
            raise ValidationError(detail="Does not exist Room id.")

class RequestCheckingView(viewsets.ReadOnlyModelViewSet):
    serializer_class = FriendsParticipationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            request_id = self.request.GET['request']
        except KeyError:
            raise ValidationError(detail="Request id가 없습니다.")
        if len(self.request.GET) > 1 :
            raise ValidationError(detail="요청 보낸 데이터가 많습니다.")
        # req_instance = FriendsParticipation.objects.filter(Q(id=request_id)).first()
        try:
            req_instance = FriendsParticipation.objects.get(Q(id=request_id))
        except FriendsParticipation.DoesNotExist:
            raise ValidationError(detail="해당 요청의 ID가 존재하지 않습니다.")

        if req_instance.user_role != 'inviter' :
            raise ValidationError(detail="해당 요청의 유저 역할이 초대자가 아닙니다.")
        if req_instance.user.kakao_auth_id != self.request.user.kakao_auth_id :
            raise ValidationError(detail="초대자의 아이디와 해당 요청 아이디와 다릅니다.")
        
        return FriendsParticipation.objects.filter(Q(room=req_instance.room) & Q(party_number=req_instance.party_number)).exclude(Q(user=self.request.user))

class SelectedRequestMatchingView(viewsets.ReadOnlyModelViewSet, mixins.UpdateModelMixin):
    serializer_class = SelectedParticipationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            request_id = self.request.GET['request']
            _request = FriendsParticipation.objects.get(Q(id=request_id))
            queryset = FriendsParticipation.objects.filter(Q(room=_request.room)).exclude(Q(party_number=_request.party_number)).exclude(Q(is_accepted='w')).values('party_number').annotate(request_count=Count('party_number')).filter(request_count__exact=_request.room.user_limit).all()
            party_number = []
            for e in queryset: 
                party_number.append(e['party_number'])
            queryset = FriendsParticipation.objects.filter(party_number__in=party_number)
            return queryset
        except KeyError:
            raise ValidationError(detail="Does not request id. Please put request id")

    def update(self, request, *args, **kwargs):
        selectedRequest = FriendsParticipation.objects.filter(Q(party_number=kwargs['pk']))
        if len(selectedRequest) == 0:
            return Response({"detail" : "요청한 Party number는 존재하지 않습니다.", "error" : 404}, status=status.HTTP_404_NOT_FOUND)
        
        # print(selectedRequest.first().party_number)
        party_number = selectedRequest.first().party_number
        room = selectedRequest.first().room
        
        # party_number = selectedRequest.party_number
        # room = selectedRequest.room

        # if FriendsParticipation.objects.filter(Q(room=room.id) & Q(user=request.user)).first().user_role != 'inviter' :
        try:
            request = FriendsParticipation.objects.get(Q(room=room.id) & Q(user=request.user))
            if request.user_role != 'inviter' or  request.type != 'c':
                return Response({"detail" : "요청한 User가 초대자가 아닙니다.", "error" : 405}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except FriendsParticipation.DoesNotExist:
            return Response({"detail" : "요청에 대한 데이터가 없습니다.", "error" : 405}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        selectedRequest = FriendsParticipation.objects.filter(Q(party_number=party_number)).all()
        
        for req in selectedRequest:
            if(req.is_accepted != 'a') :
                return Response({"detail" : "모든 유저가 수락하지 않은 요청 데이터입니다.", "error" : 405}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
        rejectedUserFcmList = []
        matchedUserFcmList = []
        d = {
            "is_accepted" : "r"
        }
        otherRequest = FriendsParticipation.objects.filter(Q(room=room)).exclude(Q(party_number=party_number)).exclude(Q(type='c'))
        otherRequest.update(**d)
        for e in otherRequest:
            rejectedUserFcmList.append(e.user.fcmToken)
        if len(rejectedUserFcmList) != 0:
            # send(rejectedUserFcmList, "요청한 미팅이 거절되었습니다.", "요청한 미팅이 거절되었습니다.")
            pass
        
        updatedData = {
            'status' : 'm'
        }
        Room.objects.filter(Q(id=room.id)).update(**updatedData)
        for e in selectedRequest:
            # user = User.objects.filter(Q(kakao_auth_id=e.user.kakao_auth_id)).first()
            user = User.objects.get(Q(kakao_auth_id=e.user.kakao_auth_id))
            meetingInfo = {
                "room" : room,
                "user" : user,
                "type" : e.type,
                "user_role" : 'g'
            }
            Meeting.objects.create(**meetingInfo)
            matchedUserFcmList.append(e.user.fcmToken)
        # send(matchedUserFcmList, "요청한 미팅이 매칭되었습니다.", "요청한 미팅이 매칭되었습니다.")

        return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

class RequestUserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ParticipatiedUserSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        try:
            request_id = self.request.GET['request']
            # request = FriendsParticipation.objects.filter(Q(id=request_id)).first()
            request = FriendsParticipation.objects.get(Q(id=request_id))
            room_id = request.room.id
            party_number = request.party_number
            queryset = FriendsParticipation.objects.select_related('user').filter(Q(room=room_id) & ~Q(user=self.request.user) & Q(party_number=party_number))
            return queryset
        except KeyError :
            raise ValidationError(detail="Put request Id")
        except FriendsParticipation.DoesNotExist:
            raise ValidationError(detail="Not Found request")

class RequestRoomViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        try:
            request = FriendsParticipation.objects.get(Q(id=self.request.GET['request']))
            # print(self.request.GET, self.request.data, self.kwargs, self.args)
            queryset = Room.objects.filter(Q(id=request.room.id))
            # print(queryset.query)
            return queryset
            # return FriendsParticipation.objects.select_related('room').all()
        except KeyError :
            raise ValidationError(detail="Put request Id")
        except FriendsParticipation.DoesNotExist:
            raise ValidationError(detail="Not Found request")
    

class InviteeParcitipateRequestViewSet(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet) :
    serializer_class = ParticipationRoomUserSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return FriendsParticipation.objects.select_related('room', 'user').filter(user=self.request.user, type='p', user_role='invitee').exclude(room__status='c')
            

    def update(self, request, *args, **kwargs):
        instance = FriendsParticipation.objects.filter(Q(id=kwargs['pk'])).first()
        # room = Room.objects.filter(Q(id=instance.room.id))
        room = Room.objects.get(Q(id=instance.room.id))

        if instance.user.kakao_auth_id != str(request.user) :
            return Response({"detail": "User Id is different.", "error" : 401}, status=status.HTTP_401_UNAUTHORIZED)

        if instance.user_role != 'invitee' :
            return Response({"detail": "User is inviter.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

        if instance.type != 'p' :
            return Response({"detail" : "Request ID type is not 'p'.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

        if instance.is_accepted != 'w' :
            return Response({"detail" : "You have already responded, or someone on your team has declined.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

        # if room.first().status == 'c' :
        if room.status == 'c' :
            return Response({"detail" : "The requested room has been cancelled.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

        # if room.first().status == 'm' :
        if room.status == 'm' :
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

        allRequestList = FriendsParticipation.objects.filter(Q(room=room.id) & Q(type='p')).all()

        if request.data["is_accepted"] == 'r' :
            fcmList = []
            for e in allRequestList:
                updatedData = {
                    "is_accepted" : 'r'
                }
                e.update(**updatedData)
                fcmList.append(e.user.fcmToken)
            fcmList.remove(instance.user.fcmToken)
            # send(fcmList, "참여 요청이 거절되었습니다.", instance.user.name + "님께서 참여 요청을 거절하였습니다.")
            
            return Response(RoomSerializer(room.first()).data, status=status.HTTP_205_RESET_CONTENT)

        
        isAllAccept = True
        fcmList = []
        for e in allRequestList:
            isAllAccept &= (e.is_accepted == 'a')
            fcmList.append(e.user.fcmToken)

        if isAllAccept :
            fcmList.remove(instance.user.fcmToken)
            # send(fcmList, "참여 요청이 모두 수락되었습니다.", "참여 요청이 모두 수락되었습니다.\n방 생성자가 수락하게 되면 최종적으로 미팅이 매칭됩니다.")
            

        return Response(serializer.data, status=status.HTTP_200_OK)

class InviteeCreateRequestViewSet(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet) :
    serializer_class = ParticipationRoomUserSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
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

            # if Room.objects.filter(Q(id=instance.room.id)).first().status == 'c' :
            if Room.objects.get(Q(id=instance.room.id)).status == 'c' :
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
            # room = Room.objects.get(Q(id=instance.room.id))
            if request.data["is_accepted"] == 'r' :
                updatedData = {
                    "status" : 'c'
                }
                room.update(**updatedData)
                # return Response(RoomSerializer(room.first()).data, status=status.HTTP_205_RESET_CONTENT)
                return Response(RoomSerializer(room).data, status=status.HTTP_205_RESET_CONTENT)
            
            allRequestList = FriendsParticipation.objects.filter(Q(room=instance.room.id) & Q(type='c')).all()
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
                    # user = User.objects.filter(Q(kakao_auth_id=e.user.kakao_auth_id)).first()
                    user = User.objects.get(Q(kakao_auth_id=e.user.kakao_auth_id))
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
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = FriendsParticipation.objects.select_related('room', 'user').filter(user=self.request.user, type='p', user_role='inviter').exclude(room__status='c')
        return queryset
            

    def create(self, request, *args, **kwargs):
        participation_user_list = request.data.pop('participation_user_list')
        if len(set(participation_user_list)) != len(participation_user_list) :
            return Response({"detail" : "Duplicate users have been added.", "error" : "404"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            room = Room.objects.get(Q(id=request.data["room"]))
        except Room.DoesNotExist:
            return Response({"detail" : 'Room ID does not exist.', "error" : 404}, status=status.HTTP_404_NOT_FOUND)
        
        instanceList = []
        if len(participation_user_list)+1 > room.user_limit:
            return Response({"detail": "You have exceeded the room limit.", "error" : "400"}, status=status.HTTP_400_BAD_REQUEST)

        if len(participation_user_list)+1 < room.user_limit:
            return Response({"detail": "There are fewer people than the room limit.", "error" : "400"}, status=status.HTTP_400_BAD_REQUEST)
        
        for user_id in participation_user_list :
            if request.user == user_id:
                return Response({"detail":"The invited user and the invited user are the same.",
                "error" : "400"}, status=status.HTTP_400_BAD_REQUEST)
            # instance = User.objects.filter(Q(kakao_auth_id=user_id)).first()
            instance = User.objects.get(Q(kakao_auth_id=user_id))
            if(instance == None) :
                return Response({"detail" : "This user does not exist.", "error" : "400"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                instanceList.append(instance)

        # inviter = User.objects.filter(Q(kakao_auth_id=request.user)).first()
        inviter = User.objects.get(Q(kakao_auth_id=request.user))

        # participatedRoom = Room.objects.filter(Q(id=request.data["room"])).first()
        participatedRoom = Room.objects.get(Q(id=request.data["room"]))

        instanceList.append(inviter)

        request.data.update({
            "room" : participatedRoom,
            "type" : 'p',
            "party_number" : str(participatedRoom.id) + inviter.kakao_auth_id
        })

        for instance in instanceList:
            request.data.update({
                'user' : instance,
                'is_accepted' : 'w' if instance.kakao_auth_id != str(request.user) else 'a',
                'user_role' : 'invitee' if instance.kakao_auth_id != str(request.user) else 'inviter'
            })
            instance = FriendsParticipation.objects.create(**request.data)

        return Response(ParticipationRoomUserSerializer(instance).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        party_number = kwargs['pk']
        instances = FriendsParticipation.objects.filter(Q(party_number=party_number))
        for instance in instances:
            self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class InviterCreateRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ParticipationRoomUserSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return FriendsParticipation.objects.select_related('room', 'user').filter(user=self.request.user, type='c', user_role='inviter').exclude(room__status='c')