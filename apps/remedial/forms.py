from django import forms
from .models import RemedialClass, RemedialAttendance
from apps.resources.models import CampusFaculty, Course, CampusClassroom
from apps.attendance.models import Student

class RemedialClassForm(forms.ModelForm):
    faculty = forms.ModelChoiceField(queryset=CampusFaculty.objects.all(), empty_label="Select Faculty")
    course = forms.ModelChoiceField(queryset=Course.objects.all(), empty_label="Select Course")
    room = forms.ModelChoiceField(queryset=CampusClassroom.objects.all(), empty_label="Select Classroom", required=False)

    class Meta:
        model = RemedialClass
        fields = ['course', 'faculty', 'date', 'start_time', 'end_time', 'room', 'remedial_code']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class RemedialAttendanceForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=Student.objects.all(), empty_label="Select Student")
    remedial_class = forms.ModelChoiceField(queryset=RemedialClass.objects.all(), empty_label="Select Remedial Class")

    class Meta:
        model = RemedialAttendance
        fields = ['remedial_class', 'student', 'attended']
