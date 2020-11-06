from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.manager import BaseManager

# class RoomManager(BaseManager) :
#     def create_room(self, meeting_date, available_dates, user_limit, introduction, status):
#         room = self.model(
#             meeting_date = meeting_date,
#             available_dates = available_dates,
#             user_limit = user_limit,
#             introduction = introduction,
#             status = status
#         )
#         return room

# class MeetingManager(BaseManager) :
#     def create_meeting(self, room_id, user_id, user_role, type):
#         meeting = self.model(
#             room_id = room_id,
#             user_id = user_id,
#             user_role = user_role,
#             type = type
#         )

#         return meeting
        
class Room(models.Model):
    STATUS_WATING = 'w'
    STATUS_MATCHED = 'm'
    STATUS_ACTIVE = 'a'
    STATUS_CANCELED = 'c'
    CHOICE_STATUS = (
        (STATUS_WATING, 'wating'),
        (STATUS_MATCHED, 'matched'),
        (STATUS_ACTIVE, 'active'),
        (STATUS_CANCELED, 'canceled'),
    )

    reg_time = models.DateTimeField(auto_now_add=True, )
    upd_time = models.DateTimeField(auto_now=True)
    available_dates = ArrayField(models.DateField())
    user_limit = models.IntegerField(default=2)
    introduction = models.CharField(default='', max_length=100)
    status = models.CharField(default='w', max_length=1, choices=CHOICE_STATUS)  # wating / matched
    
    meeting = models.ManyToManyField("user.User", through='Meeting', related_name="meeting")
    friends_participation = models.ManyToManyField('user.User', through='FriendsParticipation', related_name="friends_participation")
    # objects = RoomManager()

class Meeting(models.Model):
    USER_ROLE_ADMIN = 'a'
    USER_ROLE_GUEST = 'g'
    CHOICES_ROLE = (
        (USER_ROLE_ADMIN, '관리자'),
        (USER_ROLE_GUEST, '참여자'),
    )

    TYPE_REQUEST = 'p'
    TYPE_CREATE = 'c'
    CHOICES_TYPE = (
        (TYPE_REQUEST, '신청'),
        (TYPE_CREATE, '생성'),
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="meeting_room_id")
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="meeting_user_id")
    user_role = models.CharField(max_length=1, choices=CHOICES_ROLE)
    type = models.CharField(max_length=1, choices=CHOICES_TYPE)

    # objects = MeetingManager()

    class Meta:
        unique_together = (("room", "user"),)


class FriendsParticipation(models.Model) :
    TYPE_PARTICIPATE = 'p'
    TYPE_CREATE = 'c'
    CHOICES_TYPE = (
        (TYPE_PARTICIPATE, '신청'),
        (TYPE_CREATE, '생성'),
    )

    REQUEST_ACCEPTED = 'a'
    REQUEST_REJECTED = 'r'
    REQUEST_WAITING = 'w'
    CHOICES_REQUEST = (
        (REQUEST_ACCEPTED, '수락'),
        (REQUEST_REJECTED, '거절'),
        (REQUEST_WAITING, '대기'),
    )

    USER_ROLE_INVITER = 'inviter'
    USER_ROLE_INVITEE = 'invitee'
    CHOICES_ROLE = (
        (USER_ROLE_INVITER, 'Inviter'),
        (USER_ROLE_INVITEE, 'Invitee'),
    )
    
    room = models.ForeignKey("meeting.Room", on_delete=models.CASCADE, related_name="request_room_id")
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="request_user_id")
    
    type = models.CharField(max_length=1, choices=CHOICES_TYPE)
    is_accepted = models.CharField(default='w', max_length=1, choices=CHOICES_REQUEST)
    user_role = models.CharField(max_length=7, choices=CHOICES_ROLE)
    party_number = models.CharField(max_length=30)
    class Meta:
        unique_together = (("room", "user"))
    