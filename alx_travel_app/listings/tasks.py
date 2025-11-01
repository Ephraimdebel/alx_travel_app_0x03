from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_booking_confirmation(email, booking_reference):
    subject = "Booking Confirmation"
    message = f"Your booking with reference {booking_reference} has been successfully created!"
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(subject, message, from_email, [email])
    return "Email sent successfully"
