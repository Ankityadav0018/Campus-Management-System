from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from datetime import datetime, timedelta

@login_required
def home(request):
    """Role-based home page with student-specific dashboard"""
    user = request.user
    context = {'user': user}
    
    if user.role == 'student':
        # Student Dashboard - Show only relevant information
        from apps.attendance.models import Student, Attendance
        from apps.food.models import Order
        
        try:
            student = Student.objects.get(email=user.email)
            
            # Get attendance statistics
            attendance_stats = Attendance.objects.filter(student=student).aggregate(
                total=Count('id'),
                present=Count('id', filter=Q(status='present'))
            )
            
            total_classes = attendance_stats['total'] or 0
            present_classes = attendance_stats['present'] or 0
            attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
            
            # Get recent attendance records
            recent_attendance = Attendance.objects.filter(
                student=student
            ).select_related('faculty', 'course').order_by('-class_date')[:5]
            
            # Get food orders
            recent_orders = Order.objects.filter(
                student=student
            ).select_related('food_item').order_by('-order_date')[:5]
            
            total_orders = Order.objects.filter(student=student).count()
            
            # Check if face is registered
            from apps.attendance.models import StudentFace
            has_face = StudentFace.objects.filter(student=student).exists()
            
            context.update({
                'student': student,
                'total_classes': total_classes,
                'present_classes': present_classes,
                'attendance_percentage': round(attendance_percentage, 1),
                'recent_attendance': recent_attendance,
                'recent_orders': recent_orders,
                'total_orders': total_orders,
                'has_face': has_face,
                'is_student_dashboard': True,
            })
            
        except Student.DoesNotExist:
            context['student'] = None
            context['is_student_dashboard'] = True
    
    return render(request, 'home.html', context)
