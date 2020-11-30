from django.urls import path, include
from rest_framework import routers
from .views import AnimalViewSet, SchoolViewSet, MbtiViewSet, StarViewSet, ChineseZodiacViewSet, \
    StarCompatibilityViewSet, MbtiCompatibilityViewSet, ZodiacCompatibilityViewSet

router = routers.DefaultRouter()

router.register(r'profile', AnimalViewSet, basename='profile')
router.register(r'school', SchoolViewSet)
router.register(r'mbti', MbtiViewSet)
router.register(r'star', StarViewSet)
router.register(r'zodiac', ChineseZodiacViewSet)
router.register(r'compatibility/mbti',
                MbtiCompatibilityViewSet, 'mbtiCompatibility')
router.register(r'compatibility/star',
                StarCompatibilityViewSet, 'starCompatibility')
router.register(r'compatibility/zodiac',
                ZodiacCompatibilityViewSet, 'zodiacCompatibility')

urlpatterns = [
    path('', include(router.urls)),
]
