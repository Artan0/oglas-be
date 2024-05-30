from rest_framework import serializers
from .models import CustomUser, Ad, Auction, Bid, Message, Event, Wishlist, CarAd
from dj_rest_auth.registration.serializers import RegisterSerializer


class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    date_of_birth = serializers.DateField(required=False)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['first_name'] = self.validated_data.get('first_name', '')
        data['last_name'] = self.validated_data.get('last_name', '')
        data['phone_number'] = self.validated_data.get('phone_number', '')
        return data


def to_representation(self, instance):
    data = super().to_representation(instance)
    request = self.context.get('request')
    if request and request.user.is_authenticated:
        data['user_info'] = {
            'username': request.user.username,
            'email': request.user.email,
        }
    return data


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ['id', 'title', 'description', 'price', 'ad_type', 'imageUrl', 'owner', 'created_at', 'updated_at',
                  'is_active', 'address', 'location']


class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ['id', 'ad', 'starting_price', 'current_price', 'end_time', 'winner']


class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['id', 'auction', 'bidder', 'bid_amount', 'bid_time', 'is_highest_bid']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'read']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'location', 'host']


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'ad', 'added_date']


class CarAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarAd
        fields = ['id', 'title', 'description', 'price', 'ad_type', 'imageUrl', 'owner', 'created_at', 'updated_at',
                  'is_active', 'address', 'location', 'manufacturer', 'year', 'mileage', 'color', 'fuel_type',
                  'car_type']
