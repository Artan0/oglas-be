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

from oglas.views import AdViewSet, WishlistViewSet, \
    CustomConfirmEmailView, CustomRegisterView, get_authenticated_user_info, UserProfileUpdateView, get_choices, \
    UserAdsViewSet, AdListView, AdDetailsView, DeleteAdView, edit_ad, AddToWishlist, WishlistView, RemoveFromWishlist, \
    FeaturedAdsView, SimilarAdsView

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
    path('edit-profile/', UserProfileUpdateView.as_view(), name='user-profile-update'),
    path('api/choices/', get_choices, name='get_choices'),
    path('ad/add/', AdViewSet.as_view({'post': 'create'}), name='ad-add'),
    path('user-ads/', UserAdsViewSet.as_view({'get': 'list'}), name='user-ads'),
    path('ads/', AdListView.as_view(), name='ad-list'),
    path('ad/<int:id>/', AdDetailsView.as_view(), name='ad-details'),
    path('ad/edit/<int:ad_id>/', edit_ad, name='ad-edit'),
    path('ad/delete/<int:pk>/', DeleteAdView.as_view(), name='ad-delete'),
    path('wishlist/add/', AddToWishlist.as_view(), name='add_to_wishlist'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/remove/<int:ad_id>/', RemoveFromWishlist.as_view(), name='remove_from_wishlist'),
    path('ads/featured/', FeaturedAdsView.as_view(), name='featured-ads'),
    path('ads/similar/<int:ad_id>/', SimilarAdsView.as_view(), name='similar-ads'),

]
