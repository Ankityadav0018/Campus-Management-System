from django import forms
from .models import Faculty, Student, Attendance


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
    faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.all(),
        empty_label="Select Faculty",
        required=False
    )

    class Meta:
        model = Attendance
        fields = ['student', 'date', 'present', 'faculty']
        labels = {
            'student': 'Student',
            'date': 'Date',
            'present': 'Present',
            'faculty': 'Faculty',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['faculty_id', 'name', 'department']
        labels = {
            'faculty_id': 'Faculty ID',
            'name': 'Full Name',
            'department': 'Department',
        }
        widgets = {
            'faculty_id': forms.TextInput(attrs={'placeholder': 'Enter Faculty ID'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter Full Name'}),
            'department': forms.TextInput(attrs={'placeholder': 'Enter Department'}),
        }
        