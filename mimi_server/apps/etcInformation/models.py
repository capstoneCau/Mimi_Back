from django.db import models
# Create your models here.
class Animal(models.Model):
    imgData = models.ImageField()
    label = models.CharField(max_length=10)

class School(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    email_info = models.CharField(max_length=20)

class Mbti(models.Model):
    name = models.CharField(max_length=6, primary_key=True)
    description = models.TextField()

    compatibility = models.ManyToManyField('self', symmetrical=False, through='MbtiCompatibility')

class Star(models.Model):
    name = models.CharField(max_length=10, primary_key=True)
    start_date = models.CharField(max_length=5)
    end_date = models.CharField(max_length=5)

    compatibility = models.ManyToManyField('self', symmetrical=False, through='StarCompatibility')

class ChineseZodiac(models.Model):
    name = models.CharField(max_length=10, primary_key=True)
    order = models.IntegerField()

    compatibility = models.ManyToManyField('self', symmetrical=False, through='ZodiacCompatibility')

class MbtiCompatibility(models.Model):
    """
    MBTI 궁합도
    """
    _from = models.ForeignKey(
        Mbti,
        on_delete=models.CASCADE,
        related_name='relations_by_from_mbti',
    )
    _to = models.ForeignKey(
        Mbti,
        on_delete=models.CASCADE,
        related_name='relations_by_to_mbti',
    )
    compatibility = models.IntegerField()

class StarCompatibility(models.Model):
    """
    Star(별자리) 궁합도
    """
    _from = models.ForeignKey(
        Star,
        on_delete=models.CASCADE,
        related_name='relations_by_from_star',
    )
    _to = models.ForeignKey(
        Star,
        on_delete=models.CASCADE,
        related_name='relations_by_to_star',
    )
    compatibility = models.IntegerField()

class ZodiacCompatibility(models.Model):
    """
    Chinese zodiac(띠) 궁합도
    """
    _from = models.ForeignKey(
        ChineseZodiac,
        on_delete=models.CASCADE,
        related_name='relations_by_from_zodiad',
    )
    _to = models.ForeignKey(
        ChineseZodiac,
        on_delete=models.CASCADE,
        related_name='relations_by_to_zodiad',
    )
    compatibility = models.IntegerField()
