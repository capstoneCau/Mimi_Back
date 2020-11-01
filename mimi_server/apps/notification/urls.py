from django.urls import path
from . import views

urlpatterns = [
    path('', views.sendNotification, name = 'notification'),
]