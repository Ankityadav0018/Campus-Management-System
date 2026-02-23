from django.urls import path
from . import views

app_name = 'attendance'
urlpatterns = [
    path('', views.attendance_home, name='attendance_home'),
    path('add-student/', views.add_student, name='add_student'),
    path('summary/', views.attendance_summary, name='attendance_summary'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('register-face/', views.register_face, name='register_face'),
    path('register-face/<int:student_id>/', views.register_face, name='register_face_student'),
    path('start-face-attendance/', views.start_face_attendance, name='start_face_attendance'),
    path('video-feed/', views.video_feed, name='video_feed'),
    path('capture-attendance/', views.capture_attendance, name='capture_attendance'),
    path('absentee-alerts/', views.absentee_alerts, name='absentee_alerts'),
    path('student-list/', views.student_list, name='student_list'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('delete-face/<int:student_id>/', views.delete_face, name='delete_face'),
    path('records/', views.attendance_records, name='attendance_records'),
    path('faculty-attendance-history/', views.faculty_attendance_history, name='faculty_attendance_history'),
]
