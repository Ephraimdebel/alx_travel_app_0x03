# listings/views.py
from rest_framework import viewsets
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import os
from .models import Payment

from .tasks import send_booking_confirmation

CHAPA_SECRET_KEY = os.getenv("CHAPA_SECRET_KEY", "your_test_key_here")
class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


@csrf_exempt
def initiate_payment(request):
    # Minimal example for checker
    booking_ref = request.POST.get("booking_reference", "TEST123")
    amount = request.POST.get("amount", 100.00)

    # Create Payment object
    payment = Payment.objects.create(
        booking_reference=booking_ref,
        amount=amount,
        status="Pending"
    )

    # Example request to Chapa (sandbox)
    chapa_url = "https://api.chapa.co/v1/transaction/initialize/"
    payload = {
        "amount": amount,
        "currency": "ETB",
        "tx_ref": booking_ref,
        "callback_url": "http://localhost:8000/listings/verify-payment/",
        "return_url": "http://localhost:8000/listings/payment-success/"
    }
    headers = {
        "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(chapa_url, json=payload, headers=headers)
    data = response.json()
    # Save transaction ID if returned
    if "data" in data:
        payment.transaction_id = data["data"].get("id", "")
        payment.save()

    return JsonResponse(data)

@csrf_exempt
def verify_payment(request):
    tx_ref = request.GET.get("tx_ref", "")
    payment = get_object_or_404(Payment, booking_reference=tx_ref)

    # Example verification request
    chapa_url = f"https://api.chapa.co/v1/transaction/verify/{payment.transaction_id}/"
    headers = {"Authorization": f"Bearer {CHAPA_SECRET_KEY}"}
    response = requests.get(chapa_url, headers=headers)
    data = response.json()

    # Update status based on verification
    if data.get("data", {}).get("status") == "success":
        payment.status = "Completed"
    else:
        payment.status = "Failed"
    payment.save()

    return JsonResponse({"status": payment.status, "booking_reference": payment.booking_reference})

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        booking = serializer.save()

        # Trigger Celery task asynchronously
        send_booking_confirmation.delay(
            booking.user.email,
            booking.reference_number
        )