from django.db import models

class RemedialClass(models.Model):
    course = models.ForeignKey('resources.Course', on_delete=models.CASCADE)
    faculty = models.ForeignKey('resources.CampusFaculty', on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.ForeignKey('resources.CampusClassroom', on_delete=models.SET_NULL, null=True, blank=True)
    remedial_code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f'{self.course.name} - {self.date} ({self.start_time}-{self.end_time})'

class RemedialAttendance(models.Model):
    remedial_class = models.ForeignKey(RemedialClass, on_delete=models.CASCADE)
    student = models.ForeignKey('attendance.Student', on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    date_recorded = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('remedial_class', 'student')

    def __str__(self):
        return f'{self.student.name} attended {self.remedial_class.course.name}'
