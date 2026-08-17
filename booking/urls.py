from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/check-availability/', views.check_availability_api, name='check_availability'),
    path('api/create-booking/', views.create_booking_api, name='create_booking'),
]
