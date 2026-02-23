from django.urls import path
from . import views

urlpatterns = [
    path('', views.food_ordering_home, name='food_ordering_home'),
    path('place-order/', views.place_order, name='place_order'),
    path('rush-prediction/', views.rush_prediction, name='rush_prediction'),
    # Add more URL patterns for food ordering features here
]
