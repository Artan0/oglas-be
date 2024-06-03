from allauth.account.views import ConfirmEmailView
from dj_rest_auth.registration.views import RegisterView
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework import viewsets, request, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters import rest_framework as filters

from .models import Ad, Auction, Bid, Message, Event, Wishlist, CarAd
from .serializer import AdSerializer, AuctionSerializer, BidSerializer, MessageSerializer, EventSerializer, \
    WishlistSerializer, CustomRegisterSerializer, UserProfileUpdateSerializer, UserInfoSerializer, CarAdSerializer


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


class AdFilter(filters.FilterSet):
    price_from = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_to = filters.NumberFilter(field_name='price', lookup_expr='lte')
    year_from = filters.NumberFilter(field_name='year', lookup_expr='gte')
    year_to = filters.NumberFilter(field_name='year', lookup_expr='lte')
    mileage_from = filters.NumberFilter(field_name='mileage', lookup_expr='gte')
    mileage_to = filters.NumberFilter(field_name='mileage', lookup_expr='lte')

    class Meta:
        model = Ad
        fields = ['price_from', 'price_to', 'year_from', 'year_to', 'mileage_from', 'mileage_to']


class AdListView(APIView):
    permission_classes = []

    def get(self, request):
        category = request.query_params.get('category')
        location = request.query_params.get('location')
        ad_type = request.query_params.get('adType')
        from_date = request.query_params.get('fromDate')
        to_date = request.query_params.get('toDate')
        manufacturer = request.query_params.get('manufacturer')
        car_type = request.query_params.get('car_type')
        fuel_type = request.query_params.get('fuelType')
        color = request.query_params.get('color')
        year_from = request.query_params.get('yearFrom')
        year_to = request.query_params.get('yearTo')
        price_from = request.query_params.get('priceFrom')
        price_to = request.query_params.get('priceTo')
        mileage_from = request.query_params.get('mileageFrom')
        mileage_to = request.query_params.get('mileageTo')
        search_title = request.query_params.get('search')
        sort_by = request.query_params.get('sort')
        # Get all ads
        ads = Ad.objects.all()

        if category:
            ads = ads.filter(category=category)
        if location:
            ads = ads.filter(location=location)
        if ad_type:
            ads = ads.filter(ad_type=ad_type)
        if from_date:
            ads = ads.filter(created_at__gte=from_date)
        if to_date:
            ads = ads.filter(created_at__lte=to_date)
        if price_from:
            ads = ads.filter(price__gte=price_from)
        if price_to:
            ads = ads.filter(price__lte=price_to)
        if search_title:
            ads = ads.filter(title__icontains=search_title)
        if category == "car":
            car_filter = AdFilter(request.query_params, queryset=CarAd.objects.all())
            ads = car_filter.qs
            if manufacturer:
                ads = ads.filter(manufacturer=manufacturer)
            if car_type:
                ads = ads.filter(car_type=car_type)
            if fuel_type:
                ads = ads.filter(fuel_type=fuel_type)
            if color:
                ads = ads.filter(color=color)
            if year_from:
                ads = ads.filter(year__gte=year_from)
            if year_to:
                ads = ads.filter(year__lte=year_to)
            if mileage_from:
                ads = ads.filter(mileage__gte=mileage_from)
            if mileage_to:
                ads = ads.filter(mileage__lte=mileage_to)

        if sort_by:
            if sort_by == 'newest':
                ads = ads.order_by('-created_at')
            elif sort_by == 'oldest':
                ads = ads.order_by('created_at')
            elif sort_by == 'priceLowToHigh':
                ads = ads.order_by('price')
            elif sort_by == 'priceHighToLow':
                ads = ads.order_by('-price')

        paginator = UserAdsPagination()
        page_obj = paginator.paginate_queryset(ads, request)

        serializer = AdSerializer(page_obj, many=True)

        response_data = paginator.get_paginated_response(serializer.data)
        return Response(response_data.data, status=status.HTTP_200_OK)
