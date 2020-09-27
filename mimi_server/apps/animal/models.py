from django.db import models
from django.contrib.postgres.fields import ArrayField
# Create your models here.
class Animal(models.Model):
    imgData = ArrayField(ArrayField(models.BinaryField()))
    label = models.CharField(max_length=20)