from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from mimi_server.apps.user.models import User
from rest_framework import status

import requests
import json

from secret import FIREBASE_SERVER_KEY

# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sendNotification(request):
    if request.method == 'POST':
        fcmList = []
        for user in request.data['users']:
            fcmList.append(User.objects.get(Q(kakao_auth_id=user)).fcmToken)
            
        res = send(fcmList, request.data['title'], request.data['body'])
        return Response(res.json(), status=status.HTTP_200_OK)
    

def send(fcmList, title, body):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': FIREBASE_SERVER_KEY
    } 
    data = {
        "registration_ids" : fcmList,
        "notification" : {
            "title" : title,
            "body" : body,
            "content_available" : True,
            "priority" : "high"
        },
        "data" : {
            "title" : title,
            "body" : body,
            "content_available" : True,
            "priority" : "high"
        }
    }
    res = requests.post('https://fcm.googleapis.com/fcm/send', headers=headers, data=json.dumps(data))
    return res