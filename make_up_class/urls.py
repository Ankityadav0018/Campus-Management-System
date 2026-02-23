from django.urls import path
from . import views

urlpatterns = [
    path('', views.make_up_class_home, name='make_up_class_home'),
    # Add more URL patterns for make-up class features here
]
