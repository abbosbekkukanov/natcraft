from django.core.mail import send_mail
from django.conf import settings

def send_confirmation_email(email, confirmation_code):
    subject = 'Your Confirmation Code'
    message = f'Your confirmation code is: {confirmation_code}'
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [email])