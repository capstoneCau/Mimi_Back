from django.db.models import Q
from rest_framework import viewsets, status
from .models import Animal, School, Mbti, Star, ChineseZodiac, MbtiCompatibility, StarCompatibility, ZodiacCompatibility
from .serializer import AnimalSerializer, SchoolSerializer, MbtiSerializer, StarSerializer, ChineseZodiacSerializer, \
    MbtiCompatibilitySerializer, StarCompatibilitySerializer, ZodiacCompatibilitySerializer
from rest_framework.response import Response
# Create your views here.

class AnimalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer

class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    lookup_field = 'name'

class MbtiViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Mbti.objects.all()
    serializer_class = MbtiSerializer
    lookup_field = 'name'

class StarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Star.objects.all()
    serializer_class = StarSerializer
    lookup_field = 'name'

class ChineseZodiacViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChineseZodiac.objects.all()
    serializer_class = ChineseZodiacSerializer
    lookup_field = 'name'

class MbtiCompatibilityViewSet(viewsets.ReadOnlyModelViewSet) :
    queryset = MbtiCompatibility.objects.all()
    serializer_class = MbtiCompatibilitySerializer

class StarCompatibilityViewSet(viewsets.ReadOnlyModelViewSet) :
    queryset = StarCompatibility.objects.all()
    serializer_class = StarCompatibilitySerializer

class ZodiacCompatibilityViewSet(viewsets.ReadOnlyModelViewSet) :
    queryset = ZodiacCompatibility.objects.all()
    serializer_class = ZodiacCompatibilitySerializer
           
    

def getModel(_type) :
    _type = _type.lower()
    if _type == 'mbti' :
        return MbtiCompatibility
    elif _type == 'star' :
        return StarCompatibility
    elif _type == 'zodiac' :
        return ZodiacCompatibility