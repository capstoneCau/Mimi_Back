from .models import User
from rest_framework import viewsets
from rest_framework import mixins
from .serializer import UserSerializer

class UserViewSet(mixins.UpdateModelMixin, mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'kakao_auth_id'


