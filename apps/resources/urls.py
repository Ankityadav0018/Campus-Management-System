from django.urls import path
from . import views

app_name = 'resources'
urlpatterns = [
    path('', views.resources_home, name='resources_home'),
    
    # Block/Building Management URLs
    path('blocks/', views.block_list, name='block_list'),
    path('blocks/add/', views.add_block, name='add_block'),
    path('blocks/edit/<int:pk>/', views.edit_block, name='edit_block'),
    path('blocks/delete/<int:pk>/', views.delete_block, name='delete_block'),
    
    # Classroom URLs
    path('classrooms/', views.campus_classroom_list, name='campus_classroom_list'),
    path('classrooms/add/', views.add_campus_classroom, name='add_campus_classroom'),
    path('classrooms/edit/<int:pk>/', views.edit_campus_classroom, name='edit_campus_classroom'),
    path('classrooms/delete/<int:pk>/', views.delete_campus_classroom, name='delete_campus_classroom'),
    
    # Course URLs
    path('courses/', views.course_list, name='course_list'),
    path('courses/add/', views.add_course, name='add_course'),
    path('courses/edit/<int:pk>/', views.edit_course, name='edit_course'),
    path('courses/delete/<int:pk>/', views.delete_course, name='delete_course'),
    
    # Event URLs
    path('events/', views.event_list, name='event_list'),
    path('add-event/', views.add_event, name='add_event'),
    path('suggest-classrooms/', views.suggest_classrooms, name='suggest_classrooms'),
    
    # Faculty URLs
    path('faculty/', views.faculty_list, name='faculty_list'),
]
