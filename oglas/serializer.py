from rest_framework import serializers
from .models import CustomUser, Ad, Auction, Bid, Wishlist, CarAd
from dj_rest_auth.registration.serializers import RegisterSerializer


class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=False)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['first_name'] = self.validated_data.get('first_name', '')
        data['last_name'] = self.validated_data.get('last_name', '')
        data['phone_number'] = self.validated_data.get('phone_number', '')
        return data


# def to_representation(self, instance):
#     data = super().to_representation(instance)
#     request = self.context.get('request')
#     if request and request.user.is_authenticated:
#         data['user_info'] = {
#             'username': request.user.username,
#             'first_name': request.user.first_name,
#             'last_name': request.user.last_name,
#             'email': request.user.email,
#             'phone_number': request.user.phone_number,
#         }
#     return data
class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'phone_number', 'date_of_birth', 'role'
        ]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'username']


class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ['id', 'ad', 'starting_price', 'current_price', 'end_time', 'winner']


class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['id', 'auction', 'bidder', 'bid_amount', 'bid_time', 'is_highest_bid']


class AdSerializer(serializers.ModelSerializer):
    owner = UserInfoSerializer(read_only=True)
    car_details = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = '__all__'

    def create(self, validated_data):
        image_urls = validated_data.pop('image_urls', [])
        instance = super().create(validated_data)
        instance.image_urls = image_urls
        instance.save()
        return instance

    def get_car_details(self, obj):
        if obj.category == 'car':
            try:
                car_ad = CarAd.objects.get(id=obj.id)
                return CarAdSerializer(car_ad).data
            except CarAd.DoesNotExist:
                return None
        return None


class CarAdSerializer(serializers.ModelSerializer):
    owner = UserInfoSerializer(read_only=True)

    class Meta:
        model = CarAd
        fields = ['manufacturer', 'car_type', 'color', 'fuel_type', 'mileage', 'year', 'owner']


class EditCarAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarAd
        fields = '__all__'


class EditAdSerializer(serializers.ModelSerializer):
    imageUrl = serializers.ReadOnlyField()

    class Meta:
        model = Ad
        fields = '__all__'


class WishlistSerializer(serializers.ModelSerializer):
    ad = AdSerializer()

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'ad', 'added_date']
