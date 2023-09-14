from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(email, uid, token):
    subject = "Email Verification"
    message = (
        f"Welcome to blacktrust.\n\n"
        f"Your number one trusted community to share and report your scam experience.\n"
        f"Please click the following link to verify your email: {settings.FRONTEND_BASE_URL}/verified-email/{uid}/{token}/"

    )
    from_email = "officialblacktrust@gmail.com"  # Use the verified email address
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


def send_password_reset_verification_email(email, uid, token):
    subject = "Email Verification"
    message = (
        f"Welcome to blacktrust.\n\n"
        f"You have requested for a password reset.\n"
        f"If this is not you, please ignore the next process and contact blacktrust administrative.\n"
        f"Please click the following link to verify your email: {settings.FRONTEND_BASE_URL}/verified-email/{uid}/{token}/"

    )
    from_email = "officialblacktrust@gmail.com"  # Use the verified email address
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

