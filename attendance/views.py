from django.shortcuts import render, redirect
from .forms import StudentForm
from django.contrib import messages
from .models import Student, Attendance, Course
from django.db.models import Count, F

def attendance_home(request):
    return render(request, 'attendance/attendance_home.html')

def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student details added successfully!')
            return redirect('attendance_home')  # Redirect to attendance home or a success page
    else:
        form = StudentForm()
    return render(request, 'attendance/add_student.html', {'form': form})

def attendance_summary(request):
    # Define a threshold for low attendance (e.g., 75%)
    LOW_ATTENDANCE_THRESHOLD = 0.75

    students_summary = []
    for student in Student.objects.all():
        total_classes = Attendance.objects.filter(student=student).count()
        present_classes = Attendance.objects.filter(student=student, present=True).count()
        
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        is_risky = attendance_percentage < (LOW_ATTENDANCE_THRESHOLD * 100)

        students_summary.append({
            'student': student,
            'total_classes': total_classes,
            'present_classes': present_classes,
            'attendance_percentage': f'{attendance_percentage:.2f}%',
            'is_risky': is_risky,
        })
    
    return render(request, 'attendance/attendance_summary.html', {'students_summary': students_summary})
