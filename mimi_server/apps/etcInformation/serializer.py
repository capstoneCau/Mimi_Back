from rest_framework import serializers
from .models import Animal, School, Mbti, Friends, Star, ChineseZodiac, \
    MbtiCompatibility, StarCompatibility, ZodiacCompatibility

class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ['id', 'label', 'imgData']
    
class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['name', 'email_info']
    
class MbtiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mbti
        fields = ['name', 'description']

class StarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Star
        fields = ['name', 'start_date', 'end_date']

class ChineseZodiacSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChineseZodiac
        fields = ['name', 'order']

class MbtiCompatibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MbtiCompatibility
        fields = ['_from', '_to', 'compatibility']

class StarCompatibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = StarCompatibility
        fields = ['_from', '_to', 'compatibility']
class ZodiacCompatibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ZodiacCompatibility
        fields = ['_from', '_to', 'compatibility']