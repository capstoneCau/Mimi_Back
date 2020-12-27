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
        print(request.data)
        fcmList = []
        for user in request.data['users']:
            fcmList.append(User.objects.get(Q(kakao_auth_id=user)).fcmToken)

        res = send(
            fcmList, ntitle=request.data['title'], nbody=request.data['body'])
        return Response(res.json(), status=status.HTTP_200_OK)


def send(fcmList, ntitle=None, nbody=None, dtitle=None, dbody=None):

    fcmList = list(set(fcmList))
    print(fcmList, ntitle, nbody, dtitle, dbody)
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': FIREBASE_SERVER_KEY
    }
    data = {
        "registration_ids": fcmList,
    }
    if dbody == None:
        data['notification'] = {
            "title": ntitle,
            "body": nbody,
            "content_available": True,
            "priority": "high"
        }
    elif ntitle == None:
        data['data'] = {
            "title": dtitle,
            "body": dbody,
            "content_available": True,
            "priority": "high"
        }
    else:
        data['notification'] = {
            "title": ntitle,
            "body": nbody,
            "content_available": True,
            "priority": "high"
        }
        data['data'] = {
            "title": dtitle if dtitle != None else ntitle,
            "body": dbody if dbody != None else nbody,
            "content_available": True,
            "priority": "high"
        }

    res = requests.post('https://fcm.googleapis.com/fcm/send',
                        headers=headers, data=json.dumps(data))
    return res
