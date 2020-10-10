from .models import User, School, Mbti, Star
from rest_framework import viewsets
from rest_framework import mixins
from .serializer import UserSerializer, SchoolSerializer, MbtiSerializer, StarSerializer


class UserViewSet(mixins.UpdateModelMixin, mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'kakao_auth_id'

class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    lookup_field = 'name'

class MbtiViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Mbti.objects.all()
    serializer_class = MbtiSerializer
    lookup_field = 'name'

class StarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Star.objects.all()
    serializer_class = StarSerializer
    lookup_field = 'name'
