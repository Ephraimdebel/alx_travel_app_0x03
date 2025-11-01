from rest_framework import serializers
from .models import Listing, Booking, Review

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True, source='review_set')
    
    class Meta:
        model = Booking
        fields = '__all__'

class ListingSerializer(serializers.ModelSerializer):
    bookings = BookingSerializer(many=True, read_only=True, source='booking_set')

    class Meta:
        model = Listing
        fields = '__all__'
