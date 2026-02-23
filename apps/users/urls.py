from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'
urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('student-home/', views.student_home, name='student_home'),
    path('faculty-home/', views.faculty_home, name='faculty_home'),
    path('vendor-home/', views.vendor_home, name='vendor_home'),
    path('students/', views.student_list, name='student_list'),
    path('faculty/', views.faculty_list, name='faculty_list'),
    path('all-students/', views.all_students_data, name='all_students_data'),
    path('sync-faculty-profile/', views.sync_faculty_profile, name='sync_faculty_profile'),
    
    # Password reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html',
             email_template_name='users/password_reset_email.html',
             subject_template_name='users/password_reset_subject.txt',
             success_url='/users/password-reset/done/'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url='/users/password-reset-complete/'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]
