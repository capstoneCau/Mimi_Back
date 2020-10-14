# from django.urls import path, include
# from rest_framework import routers
# from .views import UserViewSet

# router = routers.DefaultRouter()

# router.register(r'users', UserViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
# ]


from django.conf.urls import url
# from rest_framework.authtoken.views import obtain_auth_token
from .views import CreateUserAPIView, LogoutUserAPIView, obtain_auth_token


urlpatterns = [
    url(r'^auth/login/$',
        obtain_auth_token,
        name='auth_user_login'),
    url(r'^auth/register/$',
        CreateUserAPIView.as_view(),
        name='auth_user_create'),
    url(r'^auth/logout/$',
        LogoutUserAPIView.as_view(),
        name='auth_user_logout')
]