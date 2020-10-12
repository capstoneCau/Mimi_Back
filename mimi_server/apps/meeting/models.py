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
    CHOICE_STATUS = (
        (STATUS_WATING, 'wating'),
        (STATUS_MATCHED, 'matched'),
        (STATUS_ACTIVE, 'active'),
    )
    reg_time = models.DateTimeField(auto_now_add=True, )
    upd_time = models.DateTimeField(auto_now=True)
    available_dates = ArrayField(models.DateField())
    user_limit = models.IntegerField(default=2)
    introduction = models.CharField(default='', max_length=100)
    status = models.CharField(default='w', max_length=1, choices=CHOICE_STATUS)  # wating / matched
    
    meeting = models.ManyToManyField("user.User", through='Meeting', related_name="meeting")

    # objects = RoomManager()

class Meeting(models.Model):
    USER_ROLE_ADMIN = 'a'
    USER_ROLE_GUEST = 'g'
    CHOICES_ROLE = (
        (USER_ROLE_ADMIN, '관리자'),
        (USER_ROLE_GUEST, '참여자'),
    )

    TYPE_REQUEST = 'r'
    TYPE_CREATE = 'c'
    CHOICES_TYPE = (
        (TYPE_REQUEST, '요청'),
        (TYPE_CREATE, '생성'),
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="meeting_room_id")
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="meeting_user_id")
    user_role = models.CharField(max_length=1, choices=CHOICES_ROLE)
    type = models.CharField(max_length=1, choices=CHOICES_TYPE)

    # objects = MeetingManager()

    class Meta:
        unique_together = (("room", "user"),)

    