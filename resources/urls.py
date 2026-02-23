from django.urls import path
from . import views

urlpatterns = [
    path('', views.resources_home, name='resources_home'),
    path('add-event/', views.add_event, name='add_event'),
    path('suggest-classrooms/', views.suggest_classrooms, name='suggest_classrooms'),
    # Add more URL patterns for resource management features here
]
