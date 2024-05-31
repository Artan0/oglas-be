from django.shortcuts import render

from rest_framework import viewsets, permissions, request
from rest_framework.exceptions import ValidationError

from .models import Ad, Auction, Bid, Message, Event, Wishlist, CarAd
from .serializer import AdSerializer, AuctionSerializer, BidSerializer, MessageSerializer, EventSerializer, \
    WishlistSerializer, CustomRegisterSerializer, UserProfileUpdateSerializer, UserInfoSerializer
from allauth.account.views import ConfirmEmailView
from dj_rest_auth.registration.views import RegisterView

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['GET'])
def get_authenticated_user_info(request):
    user = request.user
    serializer = UserInfoSerializer(user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_choices(request):
    cities = Ad.CITY_CHOICES
    ad_types = Ad.AD_TYPES
    categories = Ad.CATEGORY_CHOICES
    manufacturers = CarAd.MANUFACTURER_CHOICES

    return Response({
        'cities': cities,
        'ad_types': ad_types,
        'categories': categories,
        'manufacturers': manufacturers,
    })


class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer


class CustomConfirmEmailView(ConfirmEmailView):
    def get(self, request, *args, **kwargs):
        self.object = confirmation = self.get_object()
        confirmation.confirm(request)
        user = confirmation.email_address.user
        user.is_verified = True
        user.save()
        return render(request, "account/email/email_confirmed_template.html")

    def post(self, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        ad = serializer.save(owner=self.request.user)
        if self.request.data.get('category') == 'car':
            car_data = self.request.data
            CarAd.objects.create(ad=ad, **car_data)
