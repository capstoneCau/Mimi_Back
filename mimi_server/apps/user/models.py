from django.db import models
from django.contrib.auth.models import (AbstractUser, BaseUserManager)
# Create your models here.
class UserManager(BaseUserManager):

    def create_user(self, kakao_auth_id, name, gender, birthday, email, school, profileImg=None, mbti=None, star=None, chinese_zodiac=None):
        user = self.model(
            kakao_auth_id=kakao_auth_id,
            name=name,
            gender=gender,
            birthday=birthday,
            email=email,
            school=school,
            profileImg=profileImg,
            mbti=mbti,
            star=star,
            chinese_zodiac=chinese_zodiac,
        )

        return user

    def create_superuser(self, kakao_auth_id, name, gender, birthday, email, school, profileImg=None, mbti=None, star=None, chinese_zodiac=None ):
        user = self.create_user(kakao_auth_id, name, gender, birthday, email, school, profileImg, mbti, star, chinese_zodiac)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user



class User(AbstractUser):
    GENDER_MALE = 'male'
    GENDER_FEMALE = 'female'
    CHOICE_GENDER = (
        (GENDER_MALE, '남성'),
        (GENDER_FEMALE, '여성')
    )
    username = None
    kakao_auth_id = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=6, verbose_name="이름")
    gender = models.CharField(max_length=6, verbose_name="성별", choices=CHOICE_GENDER)
    birthday = models.DateField(verbose_name="생년월일")
    email = models.EmailField(unique=True, verbose_name="학교 이메일")
    school = models.CharField(max_length=40, verbose_name="학교")

    profileImg = models.ForeignKey("etcInformation.Animal", null=True, on_delete=models.CASCADE, verbose_name="프로필 사진")
    mbti = models.ForeignKey("etcInformation.Mbti", null=True, on_delete=models.CASCADE, verbose_name="mbti 성향")
    star = models.ForeignKey("etcInformation.Star", null=True, on_delete=models.CASCADE, verbose_name="별자리")
    chinese_zodiac = models.ForeignKey("etcInformation.ChineseZodiac", null=True,  on_delete=models.CASCADE, verbose_name="별자리")

    friends = models.ManyToManyField('self', symmetrical=False, through='Friends', related_name='+')
    
    USERNAME_FIELD = 'kakao_auth_id'
    REQUIRED_FIELDS = []

    # meeting_list 여태까지 한 미팅 id

    objects = UserManager()

    def __str__(self):
        return self.kakao_auth_id


class Friends(models.Model):
    """
    유저간의 관계를 정의 하는 중개 모델
    """
    RELATION_TYPE_FRIEND = 'f'
    RELATION_TYPE_BLOCK = 'b'
    CHOICES_TYPE = (
        (RELATION_TYPE_FRIEND, '친구'),
        (RELATION_TYPE_BLOCK, '차단'),
    )
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        # 자신이 from_user인 경우의 Relation목록을 가져오고 싶은 경우
        related_name='relations_by_from_user',
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        # 자신이 to_user인 경우의 Relation목록을 가져오고 싶은 경우
        related_name='relations_by_to_user',
    )
    # 서로의 관계를 표현하기 위한 필드
    type = models.CharField(default='f', max_length=1, choices=CHOICES_TYPE)


    