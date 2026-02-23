from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_home, name='attendance_home'),
    path('add-student/', views.add_student, name='add_student'),
    path('summary/', views.attendance_summary, name='attendance_summary'),
    # Add more URL patterns for attendance features here
]
