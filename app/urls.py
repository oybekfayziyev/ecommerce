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
    remove_all_item_from_card
    )

app_name = 'app'
urlpatterns = [
    # path('', views.home,name='home'),
    path('',HomeView.as_view(),name='home'),
    path('product/<slug>',ItemDetailView.as_view(),name='product'),
    path('add-to-card/<slug>',add_to_card,name='add-to-card'),
    path('add-to-card-summary/<slug>',add_to_card_summary,name='add-to-card-summary'),
    path('order-summary/',OrderSummary.as_view(),name='order-summary'),
    path('remove-from-card/<slug>',remove_from_card,name='remove-from-card'),
    path('remove-all-from-card/<slug>',remove_all_item_from_card,name='remove-all-from-card'),
    path('checkout/',Checkout.as_view(),name='checkout'),
    path('remove-single/<slug>/',remove_single_item_from_card,name='remove-single-element'),
   
]