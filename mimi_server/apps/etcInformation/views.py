from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.views import APIView
from .models import Animal, School, Mbti, Star, ChineseZodiac, MbtiCompatibility, StarCompatibility, ZodiacCompatibility
from .serializer import AnimalSerializer, SchoolSerializer, MbtiSerializer, StarSerializer, ChineseZodiacSerializer, \
    MbtiCompatibilitySerializer, StarCompatibilitySerializer, ZodiacCompatibilitySerializer
from mimi_server.apps.user.models import User
from mimi_server.apps.meeting.models import Meeting
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from mimi_server.settings import ANIMAL_IMAGE_PATH
import os
import base64
from PIL import Image
from io import BytesIO
# Create your views here.


class AnimalViewSet(viewsets.ViewSet):
    # queryset = Animal.objects.all()
    # serializer_class = AnimalSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        result = []
        if 'users' in request.GET:
            ids = request.GET['users'].split(',')
            for id in ids:
                user = User.objects.get(Q(kakao_auth_id=id))
                profile = Animal.objects.get(Q(id=user.profileImg.id))
                filename = str(profile.imgData).split("/")[2]
                imageLabel = profile.label
                path = os.path.join(os.path.join(
                    ANIMAL_IMAGE_PATH, imageLabel), filename)
                image = Image.open(path)
                image = image.resize((80, 80), Image.ANTIALIAS)
                buffered = BytesIO()
                image.save(buffered, format='JPEG')
                result.append({
                    "image": base64.b64encode(buffered.getvalue()),
                    "user": id
                })

        else:
            user = request.user
            profile = Animal.objects.get(Q(id=user.profileImg.id))
            filename = str(profile.imgData).split("/")[2]
            imageLabel = profile.label
            path = os.path.join(os.path.join(
                ANIMAL_IMAGE_PATH, imageLabel), filename)
            image = Image.open(path)
            image = image.resize((80, 80), Image.ANTIALIAS)
            buffered = BytesIO()
            image.save(buffered, format='JPEG')
            result = {
                "image": base64.b64encode(buffered.getvalue()),
            }

        return Response(result)


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    lookup_field = 'name'
    # permission_classes = [IsAuthenticatedOrReadOnly]


class MbtiViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Mbti.objects.all()
    serializer_class = MbtiSerializer
    lookup_field = 'name'
    # permission_classes = [IsAuthenticatedOrReadOnly]


class StarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Star.objects.all()
    serializer_class = StarSerializer
    lookup_field = 'name'
    # permission_classes = [IsAuthenticatedOrReadOnly]


class ChineseZodiacViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChineseZodiac.objects.all()
    serializer_class = ChineseZodiacSerializer
    lookup_field = 'name'
    # permission_classes = [IsAuthenticatedOrReadOnly]


class MbtiCompatibilityViewSet(viewsets.ViewSet):
    # queryset = MbtiCompatibility.objects.all()
    # serializer_class = MbtiCompatibilitySerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        result = []
        if len(request.GET) != 1:
            return Response({"detail": "You must send 1 data.", "error": 400}, status=status.HTTP_400_BAD_REQUEST)
        if 'users' in request.GET:
            ids = request.GET['users'].split(',')
            condition = Q(kakao_auth_id=ids.pop(0))
            for userId in ids:
                condition |= Q(kakao_auth_id=userId)
            users = User.objects.filter(condition)
            for user in users:
                compatibility = MbtiCompatibility.objects.get(
                    Q(_to=user.mbti) & Q(_from=request.user.mbti))
                print(user.mbti.name, request.user.mbti.name,
                      compatibility.compatibility)
                result.append({
                    'user': user.kakao_auth_id,
                    'mbti': user.mbti.name,
                    'compatibility': compatibility.compatibility
                })
        elif 'mbtis' in request.GET:
            mbtis = request.GET['mbtis'].split(',')
            for mbti in mbtis:
                compatibility = MbtiCompatibility.objects.get(
                    Q(_to=mbti.upper()) & Q(_from=request.user.mbti))
                print(mbti, request.user.mbti.name,
                      compatibility.compatibility)
                result.append({
                    'mbti': mbti,
                    'compatibility': compatibility.compatibility
                })
        elif 'room' in request.GET:
            meetings = Meeting.objects.filter(Q(room=request.GET['room'])).exclude(
                Q(user__gender=request.user.gender))
            for meeting in meetings:
                compatibility = MbtiCompatibility.objects.get(
                    Q(_to=meeting.user.mbti) & Q(_from=request.user.mbti))
                result.append({
                    'user': meeting.user.kakao_auth_id,
                    'mbti': meeting.user.mbti.name,
                    'compatibility': compatibility.compatibility
                })
        return Response(result, status=status.HTTP_200_OK)
    # permission_classes = [IsAuthenticatedOrReadOnly]


class StarCompatibilityViewSet(viewsets.ViewSet):
    # queryset = StarCompatibility.objects.all()
    # serializer_class = StarCompatibilitySerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        result = []
        if len(request.GET) != 1:
            return Response({"detail": "You must send 1 data.", "error": 400}, status=status.HTTP_400_BAD_REQUEST)
        if 'users' in request.GET:
            ids = request.GET['users'].split(',')
            condition = Q(kakao_auth_id=ids.pop(0))
            for userId in ids:
                condition |= Q(kakao_auth_id=userId)
            users = User.objects.filter(condition)
            for user in users:
                compatibility = StarCompatibility.objects.get(
                    Q(_to=user.star) & Q(_from=request.user.star))
                print(user.star.name, request.user.star.name,
                      compatibility.compatibility)
                result.append({
                    'user': user.kakao_auth_id,
                    'star': user.star.name,
                    'compatibility': compatibility.compatibility
                })
        elif 'stars' in request.GET:
            stars = request.GET['stars'].split(',')
            for star in stars:
                compatibility = StarCompatibility.objects.get(
                    Q(_to=star) & Q(_from=request.user.star))
                print(star, request.user.star.name,
                      compatibility.compatibility)
                result.append({
                    'star': star,
                    'compatibility': compatibility.compatibility
                })
        elif 'room' in request.GET:
            meetings = Meeting.objects.filter(Q(room=request.GET['room'])).exclude(
                Q(user__gender=request.user.gender))
            for meeting in meetings:
                compatibility = StarCompatibility.objects.get(
                    Q(_to=meeting.user.star) & Q(_from=request.user.star))
                result.append({
                    'user': meeting.user.kakao_auth_id,
                    'star': meeting.user.star.name,
                    'compatibility': compatibility.compatibility
                })
        return Response(result, status=status.HTTP_200_OK)


class ZodiacCompatibilityViewSet(viewsets.ViewSet):
    # queryset = ZodiacCompatibility.objects.all()
    # serializer_class = ZodiacCompatibilitySerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        result = []
        if len(request.GET) != 1:
            return Response({"detail": "You must send 1 data.", "error": 400}, status=status.HTTP_400_BAD_REQUEST)
        if 'users' in request.GET:
            ids = request.GET['users'].split(',')
            condition = Q(kakao_auth_id=ids.pop(0))
            for userId in ids:
                condition |= Q(kakao_auth_id=userId)
            users = User.objects.filter(condition)
            for user in users:
                compatibility = ZodiacCompatibility.objects.get(
                    Q(_to=user.chinese_zodiac) & Q(_from=request.user.chinese_zodiac))
                print(user.chinese_zodiac.name, request.user.chinese_zodiac.name,
                      compatibility.compatibility)
                result.append({
                    'user': user.kakao_auth_id,
                    'chinese_zodiac': user.chinese_zodiac.name,
                    'compatibility': compatibility.compatibility
                })
        elif 'zodiacs' in request.GET:
            print(request.GET)
            zodiacs = request.GET['zodiacs'].split(',')
            for zodiac in zodiacs:
                compatibility = ZodiacCompatibility.objects.get(
                    Q(_to=zodiac) & Q(_from=request.user.chinese_zodiac))
                # print(compatibility.query)
                print(zodiac, request.user.chinese_zodiac.name,
                      compatibility.compatibility)
                result.append({
                    'chinese_zodiac': zodiac,
                    'compatibility': compatibility.compatibility
                })
        elif 'room' in request.GET:
            meetings = Meeting.objects.filter(Q(room=request.GET['room'])).exclude(
                Q(user__gender=request.user.gender))
            for meeting in meetings:
                # print(meeting.user.chinese_zodiac, request.user.chinese_zodiac)
                compatibility = ZodiacCompatibility.objects.get(
                    Q(_to=meeting.user.chinese_zodiac) & Q(_from=request.user.chinese_zodiac))
                # print(compatibility.query)
                result.append({
                    'user': meeting.user.kakao_auth_id,
                    'chinese_zodiac': meeting.user.chinese_zodiac.name,
                    'compatibility': compatibility.compatibility
                })
        return Response(result, status=status.HTTP_200_OK)
