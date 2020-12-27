from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import viewsets, status, mixins
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework import parsers, renderers
# from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import ManualSchema

from mimi_server.firebase import registerUser
from mimi_server.apps.user.serializer import UserSerializer, UserViewSerializer, CustomAuthTokenSerializer, FriendsSerializer
from mimi_server.apps.user.models import User, Friends
from mimi_server.apps.notification.views import send


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
        registerUser(request.data['kakao_auth_id'], request.data['email'])
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
        if (request.data['fcmToken'] == None):
            return Response({"detail": "There is no fcm token.", "error": 400}, statu=status.HTTP_400_BAD_REQUEST)

        if (len(request.data) >= 2):
            return Response({"detail": "Only the fcm token can be modified.", "error": 400}, statu=status.HTTP_400_BAD_REQUEST)

        if (User.objects.filter(Q(kakao_auth_id=request.user)).first() == None):
            return Response({"detail": "The user does not exist."})

        return super.update(request, args, kwargs)


class SearchUserView(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            email = self.request.GET['email']
            queryset = User.objects.filter(
                Q(email=email) & Q(gender=self.request.user.gender))
            return queryset
        except KeyError:
            raise ValidationError("email 데이터를 넣어주세요.")


class UpdateUserView(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        raise ValidationError(detail="Not Supported")

    def update(self, request, *args, **kwargs):
        kakaoId = kwargs['pk']
        if len(request.data) > 2:
            return Response({"detail": "Too many variables.", "error": 400}, status=status.HTTP_400_BAD_REQUEST)
        if not ('mbti' in request.data and 'profileImg' in request.data):
            return Response({"detail": "Values ​​other than mbti, and profileImg were entered as data.", "error": 405}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        if request.user.kakao_auth_id != str(kakaoId):
            return Response({"detail": "You can only change your own data.", "error": 401}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = User.objects.get(Q(kakao_auth_id=str(kakaoId)))
        except User.DoesNotExist:
            return Response({"detail": "This user does not exist.", "error": 404}, status=status.HTTP_404_NOT_FOUND)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(
            user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)


class FcmTokenView(viewsets.ReadOnlyModelViewSet, mixins.UpdateModelMixin):
    serializer_class = UserSerializer

    def get_queryset(self):
        raise ValidationError(detail="Not GET")

    def update(self, request, *args, **kwargs):
        kakaoId = kwargs['pk']
        fcmToken = request.data['fcmToken']
        try:
            user = User.objects.get(Q(kakao_auth_id=str(kakaoId)))
            if user.fcmToken == fcmToken:
                return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "Not User", "error": 404}, status=status.HTTP_404_NOT_FOUND)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(
            user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser,
                      parsers.MultiPartParser, parsers.JSONParser,)
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

    def get_queryset(self):
        queryset = Friends.objects.filter(
            Q(from_user=self.request.user) & Q(type='f'))
        return queryset

    def create(self, request, *args, **kwargs):
        request.data.update({
            'from_user': request.user,
            'to_user': User.objects.get(kakao_auth_id=request.data['to_user'])
        })

        if request.data['to_user'].kakao_auth_id == request.data['from_user'].kakao_auth_id:
            return Response({"detaile": "The person to add as a friend is incorrect.", "error": 400}, status=status.HTTP_400_BAD_REQUEST)

        if len(Friends.objects.filter(Q(from_user=request.data['from_user'].kakao_auth_id) & Q(to_user=request.data['to_user'].kakao_auth_id))) > 0:
            return Response({"detaile": "Already exists.", "error": 400}, status=status.HTTP_400_BAD_REQUEST)

        friend = Friends.objects.create(**request.data)
        print(FriendsSerializer(friend).data)
        return Response(FriendsSerializer(friend).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        try:
            if request.data['type'] == None:
                return Response({"detail": "You must send type data.", "error": 400}, status=status.HTTP_400_BAD_REQUEST)
            if len(request.data) >= 2:
                return Response({"detail": "You must send only type data.", "error": 400}, status=status.HTTP_400_BAD_REQUEST)

            friends_id = kwargs['pk']
            partial = kwargs.pop('partial', False)
            instance = Friends.objects.filter(Q(id=friends_id)).first()

            if instance.type == request.data['type']:
                return Response({"detail": "It is the same type.", "error": 400}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(
                instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)

        except KeyError:
            return Response({"detail": "The url is invalid. Please enter the id in the url.", "error": 400}, status=status.HTTP_400_BAD_REQUEST)
