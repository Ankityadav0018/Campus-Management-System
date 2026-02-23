from django.contrib import admin
from .models import Block, CampusClassroom, CampusFaculty, Event, ClassroomSchedule, Course, Schedule, StudentCourseEnrollment

admin.site.register(Block)
admin.site.register(CampusClassroom)
admin.site.register(CampusFaculty)
admin.site.register(Event)
admin.site.register(ClassroomSchedule)
admin.site.register(Course)
admin.site.register(Schedule)
admin.site.register(StudentCourseEnrollment)
