from .models import Listing, Booking, User, Review
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'created_at']
        
class ReviewSerializer (serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'listing', 'rating', 'comment', 'created_at']

class ListingSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True) 
    
    class Meta:
        model = Listing
        fields = ["id", 'name', 'description', 'location', 'price_per_night', 'created_at', 'updated_at']

class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'listing', 'start_date', 'end_date', 'status', 'created_at']