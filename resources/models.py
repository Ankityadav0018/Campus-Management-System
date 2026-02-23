from django.db import models

class Block(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Classroom(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField()
    # Add other classroom-related fields as needed

    class Meta:
        unique_together = ('block', 'room_number')

    def __str__(self):
        return f'{self.block.name} - {self.room_number}'

class Faculty(models.Model):
    faculty_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    # Add other faculty-related fields as needed

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    organizer = models.CharField(max_length=100, blank=True, null=True) # e.g., Faculty name, department

    def __str__(self):
        return self.name

class ClassroomSchedule(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('classroom', 'event')

    def __str__(self):
        return f'{self.classroom} - {self.event.name}'
