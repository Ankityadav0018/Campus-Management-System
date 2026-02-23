from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    # Add other student-related fields as needed

    def __str__(self):
        return self.name

class Course(models.Model):
    course_code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=100)
    # Add other course-related fields as needed

    def __str__(self):
        return self.title

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    present = models.BooleanField(default=False)
    # Add other attendance-related fields as needed

    class Meta:
        unique_together = ('student', 'course', 'date')

    def __str__(self):
        return f'{self.student.name} - {self.course.title} - {self.date}'
