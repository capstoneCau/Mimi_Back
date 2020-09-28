from django.shortcuts import render
from mimi_server.settings import EMAIL_HOST_USER
from . import forms
from django.core.mail import send_mail
# Create your views here.
#DataFlair #Send Email
def mail(request):
    sub = forms.Mail()
    if request.method == 'POST':
        sub = forms.Mail(request.POST)
        subject = 'Welcome to DataFlair'
        message = 'Hope you are enjoying your Django Tutorials'
        recepient = str(sub['Email'].value())
        send_mail(subject, 
            message, EMAIL_HOST_USER, [recepient], fail_silently = False)
        return render(request, 'mail/success.html', {'recepient': recepient})
    return render(request, 'mail/index.html', {'form':sub})