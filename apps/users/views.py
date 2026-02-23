from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from .forms import LoginForm, UserRegisterForm
from .models import User
from .decorators import faculty_required, student_required, vendor_required

def register_user(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Auto-create Student record for every new registration
            from apps.attendance.models import Student
            import random
            try:
                # Generate unique student ID like STU2026001
                year = __import__('datetime').datetime.now().year
                existing_ids = Student.objects.filter(
                    student_id__startswith=f'STU{year}'
                ).count()
                student_id = f"STU{year}{str(existing_ids + 1).zfill(3)}"
                # Make sure it's truly unique
                while Student.objects.filter(student_id=student_id).exists():
                    student_id = f"STU{year}{str(random.randint(1000, 9999))}"

                full_name = f"{user.first_name} {user.last_name}".strip() or user.email.split('@')[0]

                Student.objects.create(
                    student_id=student_id,
                    name=full_name,
                    email=user.email,
                )
                messages.success(request, f'Account created successfully! Your Student ID is {student_id}. Please log in.')
            except Exception as e:
                messages.warning(request, f'Account created but student profile setup failed: {e}')

            return redirect('users:login')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # This is actually email due to USERNAME_FIELD
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.email}!")
                
                # Redirect based on role
                if user.role == 'student':
                    return redirect('users:student_home')
                elif user.role == 'faculty':
                    return redirect('users:faculty_home')
                elif user.role == 'vendor':
                    return redirect('users:vendor_home')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password. Please try again.")
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')

@login_required
@student_required
def student_home(request):
    """Student dashboard - only accessible by students"""
    from apps.attendance.models import Student, Attendance
    from apps.food.models import FoodOrder
    from apps.resources.models import Schedule, StudentCourseEnrollment
    from django.db.models import Q, Count
    from datetime import datetime
    
    try:
        # Get student profile
        student = Student.objects.get(email=request.user.email)
        
        # Food orders
        recent_orders = FoodOrder.objects.filter(
            student=student
        ).select_related('stall').prefetch_related('items__food_item').order_by('-time_slot')[:5]
        
        total_orders = FoodOrder.objects.filter(student=student).count()
        pending_orders = FoodOrder.objects.filter(student=student, status='pending').count()
        
        # Attendance statistics
        attendance_stats = Attendance.objects.filter(student=student).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present'))
        )
        
        total_classes = attendance_stats['total'] or 0
        present_classes = attendance_stats['present'] or 0
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        # Recent attendance records
        recent_attendance = Attendance.objects.filter(
            student=student
        ).select_related('faculty', 'course').order_by('-class_date', '-class_time')[:10]
        
        # Course-wise attendance breakdown
        enrolled_courses = StudentCourseEnrollment.objects.filter(
            student=student
        ).select_related('course')
        
        course_attendance = []
        for enrollment in enrolled_courses:
            course_stats = Attendance.objects.filter(
                student=student,
                course=enrollment.course
            ).aggregate(
                total=Count('id'),
                present=Count('id', filter=Q(status='present')),
                ai_count=Count('id', filter=Q(mode='AI')),
                manual_count=Count('id', filter=Q(mode='manual'))
            )
            
            course_total = course_stats['total'] or 0
            course_present = course_stats['present'] or 0
            course_percentage = (course_present / course_total * 100) if course_total > 0 else 0
            
            course_attendance.append({
                'course': enrollment.course,
                'total': course_total,
                'present': course_present,
                'absent': course_total - course_present,
                'percentage': round(course_percentage, 2),
                'ai_count': course_stats['ai_count'] or 0,
                'manual_count': course_stats['manual_count'] or 0,
                'is_risky': course_percentage < 75,
            })
        
        # All attendance history with pagination (50 most recent)
        attendance_history = Attendance.objects.filter(
            student=student
        ).select_related('faculty', 'course').order_by('-class_date', '-class_time')[:50]
        
        # Get student's timetable
        enrolled_course_ids = enrolled_courses.values_list('course_id', flat=True)
        
        # Get current day of week
        current_day = datetime.now().strftime('%A')
        
        # Get today's schedule
        todays_schedule = Schedule.objects.filter(
            course_id__in=enrolled_course_ids,
            day_of_week=current_day
        ).select_related('course', 'course__assigned_faculty', 'classroom', 'classroom__block').order_by('start_time')
        
        # Get full week schedule organized by day
        week_schedule = {}
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in days_order:
            day_classes = Schedule.objects.filter(
                course_id__in=enrolled_course_ids,
                day_of_week=day
            ).select_related('course', 'course__assigned_faculty', 'classroom', 'classroom__block').order_by('start_time')
            
            if day_classes.exists():
                week_schedule[day] = day_classes
        
        context = {
            'student': student,
            'recent_orders': recent_orders,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_classes': total_classes,
            'present_classes': present_classes,
            'attendance_percentage': round(attendance_percentage, 2),
            'recent_attendance': recent_attendance,
            'course_attendance': course_attendance,
            'attendance_history': attendance_history,
            'todays_schedule': todays_schedule,
            'week_schedule': week_schedule,
            'current_day': current_day,
        }
        
    except Student.DoesNotExist:
        context = {
            'student': None,
            'recent_orders': [],
            'total_orders': 0,
            'pending_orders': 0,
            'total_classes': 0,
            'present_classes': 0,
            'attendance_percentage': 0,
            'recent_attendance': [],
            'course_attendance': [],
            'attendance_history': [],
            'todays_schedule': [],
            'week_schedule': {},
            'current_day': datetime.now().strftime('%A'),
        }
    
    return render(request, 'users/student_home.html', context)

@login_required
@faculty_required
def faculty_home(request):
    """Faculty dashboard - only accessible by faculty"""
    from apps.attendance.models import Attendance, Student
    from apps.resources.models import CampusFaculty
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    # Get faculty data
    try:
        faculty = CampusFaculty.objects.get(email=request.user.email)
        
        # Get statistics
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        # Attendance stats
        total_attendance_marked = Attendance.objects.filter(faculty=faculty).count()
        attendance_this_week = Attendance.objects.filter(
            faculty=faculty, 
            class_date__gte=week_ago
        ).count()
        
        # Recent attendance records
        recent_attendance = Attendance.objects.filter(
            faculty=faculty
        ).select_related('student', 'course').order_by('-class_date')[:10]
        
        # Students with low attendance in faculty's classes
        low_attendance_students = []
        students_in_classes = Student.objects.filter(
            attendance__faculty=faculty
        ).distinct()
        
        for student in students_in_classes:
            total = Attendance.objects.filter(student=student, faculty=faculty).count()
            if total > 0:
                present = Attendance.objects.filter(
                    student=student, faculty=faculty, status='present'
                ).count()
                percentage = (present / total) * 100
                if percentage < 75:
                    low_attendance_students.append({
                        'student': student,
                        'percentage': round(percentage, 2)
                    })
        
        context = {
            'faculty': faculty,
            'total_attendance_marked': total_attendance_marked,
            'attendance_this_week': attendance_this_week,
            'recent_attendance': recent_attendance,
            'low_attendance_students': low_attendance_students[:5],
            'low_attendance_count': len(low_attendance_students),
        }
    except CampusFaculty.DoesNotExist:
        # Faculty user exists but no CampusFaculty profile
        messages.warning(request, 'Your faculty profile is being set up. Please contact admin if this persists.')
        context = {
            'faculty': None,
            'total_attendance_marked': 0,
            'attendance_this_week': 0,
            'recent_attendance': [],
            'low_attendance_students': [],
            'low_attendance_count': 0,
        }
    
    return render(request, 'users/faculty_home.html', context)

@login_required
@vendor_required
def vendor_home(request):
    """Vendor home - redirect to food vendor dashboard"""
    return redirect('food:vendor_dashboard')

@login_required
@faculty_required
def all_students_data(request):
    """View all students - accessible only by faculty and admin"""
    from apps.attendance.models import Student
    students = Student.objects.all()
    return render(request, 'users/all_students.html', {'students': students})

# Placeholder for student and faculty list views (to be implemented more fully later)
@login_required
@faculty_required
def student_list(request):
    students = User.objects.filter(role='student')
    return render(request, 'users/student_list.html', {'students': students})

@login_required
def faculty_list(request):
    faculty_members = User.objects.filter(role='faculty')
    return render(request, 'users/faculty_list.html', {'faculty_members': faculty_members})

@login_required
@faculty_required
def sync_faculty_profile(request):
    """Sync faculty user with CampusFaculty table"""
    from apps.resources.models import CampusFaculty
    
    if request.user.role != 'faculty':
        messages.error(request, 'This feature is only for faculty members.')
        return redirect('home')
    
    try:
        # Check if faculty profile already exists
        faculty = CampusFaculty.objects.get(email=request.user.email)
        messages.info(request, 'Your faculty profile is already set up!')
    except CampusFaculty.DoesNotExist:
        # Create new faculty profile
        faculty_count = CampusFaculty.objects.count()
        faculty_id = f"FAC{str(faculty_count + 1).zfill(4)}"
        
        faculty = CampusFaculty.objects.create(
            faculty_id=faculty_id,
            name=request.user.get_full_name() or request.user.email.split('@')[0],
            email=request.user.email,
            user=request.user
        )
        messages.success(request, 'Faculty profile created successfully! You can now mark attendance.')
    
    return redirect('users:faculty_home')

# Password reset views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')
