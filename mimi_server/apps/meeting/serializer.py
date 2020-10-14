from rest_framework import serializers
from collections import OrderedDict
from .models import Room, Meeting
from ..user.models import User, FriendsParticipation
from ..user.serializer import UserField

class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['id', 'room', 'user', 'user_role', 'type']
        lookup_field = 'id'

    def create(self, validated_data) :
        meeting = Meeting.objects.create(**validated_data)
        meeting.save()
        return meeting

class RoomSerializer(serializers.ModelSerializer):
    # Django REST Framework makes it possible to create a read-only field that
    # gets it's value by calling a function. In this case, the client expects
    # `serializers.SerializerMethodField` is a good way to avoid having the
    # requirements of the client leak into our API.
    reg_time = serializers.SerializerMethodField(method_name='get_reg_time')
    upd_time = serializers.SerializerMethodField(method_name='get_upd_time')
    # meeting_id = MeetingSerializer(many=True)
    class Meta:
        model = Room
        fields = ('id', 'reg_time', 'upd_time', 'available_dates', 'user_limit', 'introduction', 'status', 'meeting')
        
        lookup_field = 'pk'

    def create(self, validated_data):
        # print(validated_data)
        room = Room.objects.create(**validated_data)
        room.save()
        return room

    def get_reg_time(self, instance):
        return instance.reg_time.isoformat()

    def get_upd_time(self, instance):
        return instance.upd_time.isoformat()

class RoomField(serializers.PrimaryKeyRelatedField):

    def to_representation(self, value):
        id = super(RoomField, self).to_representation(value)
        try:
          room = Room.objects.get(pk=id)
          serializer = RoomSerializer(room)
          return serializer.data
        except Room.DoesNotExist:
            return None

    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            return {}

        return OrderedDict([(item.id, self.display_value(item)) for item in queryset])

class RoomMeetingSerializer(serializers.ModelSerializer) :
    # meetings = MeetingSerializer(many=True)
    room = RoomField(queryset=Room.objects.all())
    class Meta:
        model = Meeting
        fields = ['id', 'user', 'room']
        # fields = ('id', 'reg_time', 'upd_time', 'meeting_date', 'available_dates', 'user_limit', 'introduction', 'status', 'meeting')
        # fields = '__all__'
        # lookup_field = 'user'

class FriendsParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendsParticipation
        fields = ['id', 'room', 'from_user', 'to_user', 'type', 'is_accepted']

class ParticipationRoomUserSerializer(serializers.ModelSerializer):
    room = RoomField(queryset=Room.objects.all())
    from_user = UserField(queryset=User.objects.all())
    to_user = UserField(queryset=User.objects.all())
    class Meta:
        model = FriendsParticipation
        fields = ['id', 'type', 'is_accepted', 'room', 'from_user', 'to_user']