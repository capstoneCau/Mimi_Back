from rest_framework import serializers
from .models import User, Friends
from collections import OrderedDict
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from ..etcInformation.serializer import AnimalSerializer

class UserSerializer(serializers.ModelSerializer):
    # profileImg = AnimalSerializer()
    class Meta:
        model = User
        fields = ['kakao_auth_id', 'name', 'gender', 'birthday','email', 'school', 'fcmToken',
        'profileImg', 'mbti', 'star', 'chinese_zodiac']
        # fields = '__all__'
        lookup_field = 'kakao_auth_id'
        extra_kwargs = {
            'url': {'lookup_field': 'kakao_auth_id'}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.set_password("mimi")
        user.save()
        return user

class UserViewSerializer(serializers.ModelSerializer):
    profileImg = AnimalSerializer()
    class Meta:
        model = User
        fields = ['kakao_auth_id', 'name', 'gender', 'birthday','email', 'school', 'fcmToken',
        'profileImg', 'mbti', 'star', 'chinese_zodiac']
        lookup_field = 'kakao_auth_id'
        extra_kwargs = {
            'url': {'lookup_field': 'kakao_auth_id'}
        }

class FriendsSerializer(serializers.ModelSerializer):
    to_user = UserSerializer()
    class Meta:
        model = Friends
        fields = ['id', 'to_user', 'type']

class UserField(serializers.PrimaryKeyRelatedField):

    def to_representation(self, value):
        id = super(UserField, self).to_representation(value)
        try:
          user = User.objects.get(pk=id)
          serializer = UserSerializer(user)
          return serializer.data
        except User.DoesNotExist:
            return None

    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            return {}

        return OrderedDict([(item.kakao_auth_id, self.display_value(item)) for item in queryset])

class CustomAuthTokenSerializer(serializers.Serializer):
    kakao_auth_id = serializers.CharField(label=_("Kakao_auth_id"))

    def validate(self, attrs):
        kakao_auth_id = attrs.get('kakao_auth_id')
        password = "mimi"

        if kakao_auth_id and password:
            user = authenticate(request=self.context.get('request'),
                                kakao_auth_id=kakao_auth_id, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
