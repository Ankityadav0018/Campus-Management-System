from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import RemedialClass, RemedialAttendance
from .forms import RemedialClassForm, RemedialAttendanceForm
from datetime import date

def remedial_home(request):
    """OPTIMIZED: Use select_related to reduce queries"""
    remedial_classes = RemedialClass.objects.select_related('faculty', 'course').order_by('-date')
    total_classes = remedial_classes.count()
    upcoming_classes = RemedialClass.objects.filter(date__gte=date.today()).count()
    total_attendance = RemedialAttendance.objects.count()
    unique_students = RemedialAttendance.objects.values('student').distinct().count()
    
    context = {
        'remedial_classes': remedial_classes,
        'total_classes': total_classes,
        'upcoming_classes': upcoming_classes,
        'total_attendance': total_attendance,
        'unique_students': unique_students,
    }
    return render(request, 'remedial/remedial_home.html', context)

def add_remedial_class(request):
    if request.method == 'POST':
        form = RemedialClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Remedial Class added successfully!')
            return redirect('remedial:remedial_home')
    else:
        form = RemedialClassForm()
    return render(request, 'remedial/add_remedial_class.html', {'form': form})

def edit_remedial_class(request, pk):
    remedial_class = get_object_or_404(RemedialClass, pk=pk)
    if request.method == 'POST':
        form = RemedialClassForm(request.POST, instance=remedial_class)
        if form.is_valid():
            form.save()
            messages.success(request, 'Remedial Class updated successfully!')
            return redirect('remedial:remedial_home')
    else:
        form = RemedialClassForm(instance=remedial_class)
    return render(request, 'remedial/edit_remedial_class.html', {'form': form})

def delete_remedial_class(request, pk):
    remedial_class = get_object_or_404(RemedialClass, pk=pk)
    if request.method == 'POST':
        remedial_class.delete()
        messages.success(request, 'Remedial Class deleted successfully!')
        return redirect('remedial:remedial_home')
    return render(request, 'remedial/confirm_delete.html', {'object': remedial_class})

def remedial_attendance_list(request):
    """OPTIMIZED: Use select_related to reduce queries"""
    remedial_attendance_records = RemedialAttendance.objects.select_related(
        'remedial_class__faculty',
        'remedial_class__course',
        'student'
    ).order_by('-remedial_class__date')
    return render(request, 'remedial/remedial_attendance_list.html', {'remedial_attendance_records': remedial_attendance_records})

def mark_remedial_attendance(request):
    if request.method == 'POST':
        form = RemedialAttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Remedial Attendance marked successfully!')
            return redirect('remedial:remedial_attendance_list')
    else:
        form = RemedialAttendanceForm()
    return render(request, 'remedial/mark_remedial_attendance.html', {'form': form})
