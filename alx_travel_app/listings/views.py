from django.shortcuts import render
from rest_framework import viewsets
from .models import Listing,Booking
from .serializers import ListingSerializer,BookingSerializer


# Create your views here.

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer