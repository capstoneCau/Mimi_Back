"""DjangoRestApisPostgreSQL URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include 
urlpatterns = [
    # path('admin/', admin.site.urls),
    # url(r'^', include('mimi_server.apps.tutorials.urls')),
    path(r'api/', include('mimi_server.apps.user.auth_urls')),
    path('user/', include('mimi_server.apps.user.user_urls')),
    path('mail/', include('mimi_server.apps.mail.urls')),
    path('image/', include('mimi_server.apps.image.urls')),
    path('meeting/', include('mimi_server.apps.meeting.urls')),
    path('request/', include('mimi_server.apps.meeting.request_urls')),
    path('etcInformation/', include('mimi_server.apps.etcInformation.urls')),
    path('notification/', include('mimi_server.apps.notification.urls'))
]
