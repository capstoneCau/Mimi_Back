from rest_framework import serializers
from .models import User
from collections import OrderedDict

class UserSerializer(serializers.ModelSerializer):
    # profileImg = AnimalSerializer()
    class Meta:
        model = User
        fields = ['kakao_auth_id', 'name', 'gender', 'birthday', 'address','email', 'school',
        'profileImg', 'mbti', 'star', 'chinese_zodiac', 'kakao_id']
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