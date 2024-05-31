from django.shortcuts import render

from rest_framework import viewsets, request

from rest_framework.pagination import PageNumberPagination

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
    fuel = CarAd.FUEL_CHOICES
    color = CarAd.COLOR_CHOICES
    car_type = CarAd.CAR_TYPE_CHOICES

    return Response({
        'cities': cities,
        'ad_types': ad_types,
        'categories': categories,
        'manufacturers': manufacturers,
        'colors': color,
        'car_types': car_type,
        'fuels': fuel
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
        if ad.category == 'car':
            car_data = {
                'manufacturer': self.request.data.get('manufacturer'),
                'year': self.request.data.get('year'),
                'mileage': self.request.data.get('mileage'),
                'fuel_type': self.request.data.get('fuel_type'),
                'color': self.request.data.get('color'),
                'car_type': self.request.data.get('car_type'),
                'price': ad.price,
                'title': ad.title,
                'description': ad.description,
                'address': ad.address,
                'created_at': ad.created_at,
                'updated_at': ad.updated_at,
                'owner': ad.owner,
                'location': ad.location,
                'imageUrl': ad.imageUrl,
                'category': ad.category,
                'adType': ad.adType
            }
            CarAd.objects.create(ad_ptr_id=ad.id, **car_data)


class UserAdsPagination(PageNumberPagination):
    page_size = 9
    page_query_param = 'page'
    page_size_query_param = 'size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'total_pages': self.page.paginator.num_pages
        })


class UserAdsViewSet(viewsets.ModelViewSet):
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserAdsPagination

    def get_queryset(self):
        user = self.request.user
        return Ad.objects.filter(owner=user)
