from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)  # Added index for faster lookups

    class Meta:
        indexes = [
            models.Index(fields=['name']),  # Index for name searches
            models.Index(fields=['student_id']),  # Already unique but explicit index
        ]

    def __str__(self):
        return self.name

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    faculty = models.ForeignKey('resources.CampusFaculty', on_delete=models.CASCADE)
    course = models.ForeignKey('resources.Course', on_delete=models.CASCADE, null=True, blank=True)
    class_date = models.DateField(db_index=True)  # Added index for date filtering
    class_time = models.TimeField(null=True, blank=True)  # Start time of the class
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present', db_index=True)  # Index for status filtering
    MODE_CHOICES = (
        ('manual', 'Manual'),
        ('AI', 'AI'),
        ('remedial', 'Remedial'),
    )
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='manual')

    class Meta:
        unique_together = ('student', 'faculty', 'course', 'class_date', 'class_time')
        indexes = [
            models.Index(fields=['student', 'status']),  # Composite index for attendance percentage queries
            models.Index(fields=['class_date', 'status']),  # Index for date-based status queries
            models.Index(fields=['-class_date']),  # Index for recent records (descending order)
        ]

    def __str__(self):
        return f'{self.student.name} - {self.faculty.name} - {self.class_date} - {self.status}'

class StudentFace(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    face_encoding = models.BinaryField() # Store numpy array as binary data

    def __str__(self):
        return f'Face for {self.student.name}'

class Faculty(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    office = models.CharField(max_length=100, blank=True, null=True)                
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='faculty_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

