from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import viewsets, status, mixins
from rest_framework.views import APIView
from mimi_server.apps.user.serializer import UserSerializer, UserViewSerializer, CustomAuthTokenSerializer, FriendsSerializer
from mimi_server.apps.user.models import User, Friends
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework import parsers, renderers
# from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import ManualSchema

class CreateUserAPIView(CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # We create a token than will be used for future auth
        token = Token.objects.create(user=serializer.instance)
        token_data = {"token": token.key}
        return Response(
            {**serializer.data, **token_data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class LogoutUserAPIView(APIView):
    queryset = get_user_model().objects.all()

    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)

class UserFcmTokenView(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    def update(self, request, *args, **kwargs):
        if (request.data['fcmToken'] == None) :
            return Response({"detail" : "There is no fcm token.", "error": 400}, statu=status.HTTP_400_BAD_REQUEST)
        
        if (len(request.data) >= 2):
            return Response({"detail" : "Only the fcm token can be modified.", "error": 400}, statu=status.HTTP_400_BAD_REQUEST)

        if (User.objects.filter(Q(kakao_auth_id=request.user)).first() == None) :
            return Response({"detail" : "The user does not exist."})
        
        return super.update(request, args, kwargs)

class SearchUserView(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try :
            email = self.request.data['email']
            queryset = User.objects.filter(Q(email=email))
            return queryset
        except KeyError:
            raise ValidationError("email 데이터를 넣어주세요.")

            
class CustomAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = CustomAuthTokenSerializer
    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="kakao_auth_id",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Kakao_auth_id",
                        description="Valid Kakao_auth_id for authentication",
                    ),
                )
            ],
            encoding="application/json",
        )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'user': UserViewSerializer(User.objects.get(kakao_auth_id=user)).data, 'token': token.key})


obtain_auth_token = CustomAuthToken.as_view()

class FriendsViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = FriendsSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self) :
        queryset = Friends.objects.filter(Q(from_user=self.request.user) & Q(type='f'))
        return queryset
    
    def create(self, request, *args, **kwargs):
        request.data.update({
            'from_user' : request.user,
            'to_user' : User.objects.get(kakao_auth_id=request.data['to_user'])
        })

        if request.data['to_user'].kakao_auth_id == request.data['from_user'].kakao_auth_id :
            return Response({"detaile" : "The person to add as a friend is incorrect.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(Friends.objects.filter(Q(from_user=request.data['from_user'].kakao_auth_id) & Q(to_user=request.data['to_user'].kakao_auth_id))) > 0 :
            return Response({"detaile" : "Already exists.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

        friend = Friends.objects.create(**request.data)
        print(FriendsSerializer(friend).data)
        return Response(FriendsSerializer(friend).data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        try:
            if request.data['type'] == None:
                return Response({"detail" : "You must send type data.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)
            if len(request.data) >= 2 :
                return Response({"detail" : "You must send only type data.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)
            
            friends_id = kwargs['pk']
            partial = kwargs.pop('partial', False)
            instance = Friends.objects.filter(Q(id=friends_id)).first()

            if instance.type == request.data['type'] :
                return Response({"detail" : "It is the same type.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)

        except KeyError:
            return Response({"detail" : "The url is invalid. Please enter the id in the url.", "error" : 400}, status=status.HTTP_400_BAD_REQUEST)