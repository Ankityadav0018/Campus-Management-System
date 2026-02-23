from django.db import models

class Block(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class CampusClassroom(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, db_index=True)
    room_number = models.CharField(max_length=20, db_index=True)
    capacity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('block', 'room_number')
        ordering = ['block__name', 'room_number']
        indexes = [
            models.Index(fields=['block', 'room_number']),
        ]

    def __str__(self):
        return f'{self.block.name} - {self.room_number}'

class CampusFaculty(models.Model):
    faculty_id = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, null=True, blank=True, related_name='faculty_profile')

    class Meta:
        verbose_name_plural = "Campus Faculty"
        ordering = ['name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['faculty_id']),
        ]

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    organizer = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['start_time', 'end_time']),
            models.Index(fields=['-start_time']),
        ]

    def __str__(self):
        return self.name

class ClassroomSchedule(models.Model):
    classroom = models.ForeignKey(CampusClassroom, on_delete=models.CASCADE, related_name='schedules')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='classroom_schedules')

    class Meta:
        unique_together = ('classroom', 'event')
        indexes = [
            models.Index(fields=['classroom', 'event']),
        ]

    def __str__(self):
        return f'{self.classroom} - {self.event.name}'

class Course(models.Model):
    course_id = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    assigned_faculty = models.ForeignKey(CampusFaculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['assigned_faculty']),
        ]

    def __str__(self):
        return self.name

class Schedule(models.Model):
    """Weekly schedule for courses"""
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedules')
    classroom = models.ForeignKey(CampusClassroom, on_delete=models.CASCADE, related_name='course_schedules')
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK, db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    semester = models.CharField(max_length=20, default='Spring 2026')
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        indexes = [
            models.Index(fields=['day_of_week', 'start_time']),
            models.Index(fields=['course']),
        ]
    
    def __str__(self):
        return f'{self.course.name} - {self.day_of_week} {self.start_time}-{self.end_time}'

class StudentCourseEnrollment(models.Model):
    """Track which students are enrolled in which courses"""
    student = models.ForeignKey('attendance.Student', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolled_students')
    enrolled_date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'course')
        indexes = [
            models.Index(fields=['student', 'course']),
        ]
    
    def __str__(self):
        return f'{self.student.name} - {self.course.name}'
