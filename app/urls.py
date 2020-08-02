"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from .views import (
	HomeView,
	ItemDetailView,
    OrderSummary,  
    Checkout,
    add_to_card,
    remove_from_card,
    add_to_card_summary,
    remove_single_item_from_card,
    remove_all_item_from_card,
    PaymentView,
    add_coupon,
    RequestRefundView,
    ContactView,
    CategoryDetailView,
    OrderedItems,
    )

from . import apis

app_name = 'app'
urlpatterns = [
    # path('', views.home,name='home'),
    path('',HomeView.as_view(),name='home'),
    path('product/<slug>',ItemDetailView.as_view(),name='product'),
    path('add-to-card/<slug>',add_to_card,name='add-to-card'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('add-to-card-summary/<slug>',add_to_card_summary,name='add-to-card-summary'),
    path('order-summary/',OrderSummary.as_view(),name='order-summary'),
    path('remove-from-card/<slug>',remove_from_card,name='remove-from-card'),
    path('remove-all-from-card/<slug>',remove_all_item_from_card,name='remove-all-from-card'),
    path('checkout/',Checkout.as_view(),name='checkout'),
    path('add-coupon/',add_coupon, name='add-coupon'),
    path('remove-single/<slug>/',remove_single_item_from_card,name='remove-single-element'),
    path('payment/<payment_option>',PaymentView.as_view(),name = 'payment'),
    path('request-refund/',RequestRefundView.as_view(),name = 'request-refund'),
    path('category/<id>/<slug>/', CategoryDetailView.as_view(), name='category'),
    path('ordered/items/', OrderedItems.as_view(), name='ordered-items'),



    # APIS
    path('api/category/', apis.CategoryViewSet.as_view()),
    path('api/category/<pk>/', apis.CategoryDetailViewSet.as_view({
        'get':'retrieve', 
        'delete' : 'destroy',
        'put' : 'update'
    })),
   
]
