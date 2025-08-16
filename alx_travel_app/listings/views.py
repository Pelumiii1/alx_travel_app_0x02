import os
import uuid
import requests

from rest_framework.response import Response
from django.conf import settings
from rest_framework import viewsets
from .models import Listing,Booking, Payment
from .serializers import ListingSerializer,BookingSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny



CHAPA_SECRET_KEY = os.getenv("CHAPA_SECRET_KEY")
CHAPA_INITIATE_URL = "https://api.chapa.co/v1/transaction/initialize"

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

class InitiatePaymentView(APIView):
    
    def post (self,request):
        user = request.user
        amount = request.data.get('amount')
        booking_reference = str(uuid.uuid4())
        
        payment = Payment.objects.create(
            user = user,
            booking_reference = booking_reference, 
            amount = amount,
            status = "Pending",
        )
        
        
        
        #Chapa request data
        data = {
            "amount":amount,
            "currency":"ETB",
            "email":user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            'tx_ref': booking_reference,
            "callback_url": f"http://localhost:8000/api/payments/verify/{booking_reference}/",
            "return_url": "http://localhost:8000/payment-success/",
            "customization[title]": "Booking Payment",
            "customization[description]": "Payment for travel booking",
        }
        
        headers = {
            "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        
        response = requests.post(
            f"{settings.CHAPA_BASE_URL.rstrip('/')}/transaction/initialize",
            data=data,
            headers=headers,
        )
        
        resp_json = response.json()
        
        if resp_json.get('status') == 'success':
            payment.transaction_id = booking_reference
            payment.save()
            
            return Response({'payment_url':resp_json['data']['checkout_url']})
        else:
            return Response(resp_json, status=400)
        
class VerifyPaymentView(APIView):
    def get(self,request,booking_reference):
        try:
            payment = Payment.objects.get(booking_reference=booking_reference)
        except Payment.DoesNotExist:
            return Response({'error':'Payment not found'},status=404)
        
        headers = {
            "Authorization": f'Bearer {settings.CHAPA_SECRET_KEY}'
        }
        
        verify_url = f'{settings.CHAPA_BASE_URL}/transaction/verify/{booking_reference}'
        
        response = requests.get(verify_url, headers=headers)
        
        resp_json = response.json()
        
        if resp_json.get('status') == 'success' and resp_json['data']['status'] == 'success':
            payment.status = "Completed"
            payment.save()
            from django.core.mail import send_mail
            send_mail(
                'payment confirmation',
                'your booking payment was successful',
                "noreply@mytravel.com",
                [payment.user.email],
            )
            
            return Response({"message": "Payment verified successfully"})
        else:
            payment.status = "Failed"
            payment.save()
            return Response({"message": "Payment verification failed"}, status=400)