from django import forms
from .models import Event, CampusClassroom, CampusFaculty, Course, Block

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'start_time', 'end_time', 'organizer']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter event name',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter event description',
                'rows': 4
            }),
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': True
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': True
            }),
            'organizer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter organizer name'
            }),
        }
        labels = {
            'name': 'Event Name',
            'description': 'Event Description',
            'start_time': 'Start Date & Time',
            'end_time': 'End Date & Time',
            'organizer': 'Organized By',
        }

class CampusClassroomForm(forms.ModelForm):
    class Meta:
        model = CampusClassroom
        fields = ['block', 'room_number', 'capacity']
        widgets = {
            'block': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'room_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 101, 202A',
                'required': True
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter seating capacity',
                'min': 1,
                'required': True
            }),
        }
        labels = {
            'block': 'Building/Block',
            'room_number': 'Room Number',
            'capacity': 'Seating Capacity',
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_id', 'name', 'assigned_faculty']
        widgets = {
            'course_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., CS101, MATH201',
                'required': True
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter course name',
                'required': True
            }),
            'assigned_faculty': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'course_id': 'Course Code',
            'name': 'Course Name',
            'assigned_faculty': 'Assigned Faculty',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_faculty'].empty_label = "-- Select Faculty (Optional) --"
        self.fields['assigned_faculty'].required = False

class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Block A, Engineering Building',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter block description (optional)',
                'rows': 3
            }),
        }
        labels = {
            'name': 'Block/Building Name',
            'description': 'Description',
        }
