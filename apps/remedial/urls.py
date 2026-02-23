from django.urls import path
from . import views

app_name = 'remedial'
urlpatterns = [
    path('', views.remedial_home, name='remedial_home'),
    path('add-class/', views.add_remedial_class, name='add_remedial_class'),
    path('edit-class/<int:pk>/', views.edit_remedial_class, name='edit_remedial_class'),
    path('delete-class/<int:pk>/', views.delete_remedial_class, name='delete_remedial_class'),
    path('attendance/', views.remedial_attendance_list, name='remedial_attendance_list'),
    path('attendance/mark/', views.mark_remedial_attendance, name='mark_remedial_attendance'),
]
