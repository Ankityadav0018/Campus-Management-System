from django import forms
from .models import Student, Attendance
from apps.resources.models import CampusFaculty, Course

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'name', 'email']
        labels = {
            'student_id': 'Student ID',
            'name': 'Full Name',
            'email': 'Email Address',
        }
        widgets = {
            'student_id': forms.TextInput(attrs={'placeholder': 'Enter Student ID'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter Full Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email Address'}),
        }

class AttendanceForm(forms.ModelForm):
    # Dynamically populate faculty and course choices in the view if needed
    faculty = forms.ModelChoiceField(queryset=CampusFaculty.objects.all(), empty_label="Select Faculty", required=False)
    course = forms.ModelChoiceField(queryset=Course.objects.all(), empty_label="Select Course", required=False)

    class Meta:
        model = Attendance
        fields = ['student', 'faculty', 'course', 'class_date', 'status', 'mode']
        widgets = {
            'class_date': forms.DateInput(attrs={'type': 'date'}),
        }
