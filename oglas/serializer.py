from rest_framework import serializers
from .models import CustomUser, Ad, Auction, Bid, Message, Event, Wishlist


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']


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
