from django.urls import path
from . import views

app_name = 'ai_module'
urlpatterns = [
    path('', views.ai_home, name='ai_home'),
    path('face-recognition/', views.start_face_attendance_view, name='start_face_attendance'),
    path('face-recognition/video_feed/', views.video_feed_view, name='video_feed'),
    path('register-face/<str:student_id>/', views.register_face_view, name='register_face'),
    path('absentee-alert/', views.absentee_alert, name='absentee_alert'),
]
