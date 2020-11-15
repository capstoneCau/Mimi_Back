from django.shortcuts import render
from mimi_server.settings import EMAIL_HOST_USER
from . import forms
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
import random
# Create your views here.
#DataFlair #Send Email
@api_view(['POST'])
def mail(request):
    sub = forms.Mail()
    if request.method == 'POST':
        if request.data['address'] != None :
            ranNum = random.randint(100000, 999999)
            sub = forms.Mail(request.POST)
            subject = 'Welcome to Mimi'
            message = f"You input {ranNum}"
            recepient = request.data['address']
            send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently = False)
            return Response({"token": ranNum}, status=status.HTTP_201_CREATED)
        elif request.data['address'] == None :
            return Response({"error": "Not be inputted Address"}, status=status.HTTP_400_BAD_REQUEST)
    return render(request, 'mail/index.html', {'form':sub})