"""
URL configuration for oglasBE project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from oglas.views import AdViewSet, AuctionViewSet, BidViewSet, MessageViewSet, EventViewSet, WishlistViewSet, \
    CustomConfirmEmailView, CustomRegisterView, get_authenticated_user_info

router = DefaultRouter()
router.register(r'ads', AdViewSet)
router.register(r'auctions', AuctionViewSet)
router.register(r'bids', BidViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'events', EventViewSet)
router.register(r'wishlists', WishlistViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/registration/custom/', CustomRegisterView.as_view(), name='custom_register'),
    path('accounts/', include('allauth.urls')),
    path('email-confirmed/', TemplateView.as_view(template_name="account/email/email_confirmed_template.html"),
         name='email_confirmed'),
    path('accounts/confirm-email/<str:key>/', CustomConfirmEmailView.as_view(), name='account_confirm_email'),
    path('user-info/', get_authenticated_user_info, name='get_authenticated_user_info'),

]
