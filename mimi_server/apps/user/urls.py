from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet, SchoolViewSet, MbtiViewSet, StarViewSet

router = routers.DefaultRouter()

router.register(r'users', UserViewSet)
router.register(r'school', SchoolViewSet)
router.register(r'mbti', MbtiViewSet)
router.register(r'star', StarViewSet)

urlpatterns = [
    path('', include(router.urls)),
]