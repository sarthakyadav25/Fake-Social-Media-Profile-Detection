from django.conf import settings
from django.core.mail import send_mail

def send_email(email,token):
    try:
        subject = 'Click On The Link To Verfiy Email'
        message = f'Click Here http://127.0.0.1:8000/verify/{token}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        send_mail( subject, message, email_from, recipient_list )
        return True
    except Exception as e:
        print(e)
        return False
