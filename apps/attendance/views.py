from django.shortcuts import render, redirect, get_object_or_404
from .forms import StudentForm, AttendanceForm
from django.contrib import messages
from .models import Student, Attendance, StudentFace
from apps.resources.models import CampusFaculty, Course
from django.db.models import Count, F, Q, Avg, Case, When, FloatField, ExpressionWrapper
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from apps.users.decorators import faculty_required
from .face_recognition_utils import (
    load_known_faces,
    process_and_encode_face,
    generate_frames,
    recognize_faces_in_frame_fast,
    mark_attendance_for_recognized_faces,
    capture_and_recognize,
    encode_face_from_image,
    _get_deepface,
    _find_best_match,
    _detect_faces_opencv,
    _embed_cropped_face,
)
import pickle
import json
import base64
import numpy as np
import cv2
from django.conf import settings
import os
from datetime import datetime

@login_required
def attendance_home(request):
    """Attendance home - OPTIMIZED with database aggregation"""
    if request.user.role == 'student':
        try:
            student = Student.objects.get(email=request.user.email)
            
            # Use aggregation to count in one query
            attendance_stats = Attendance.objects.filter(student=student).aggregate(
                total=Count('id'),
                present=Count('id', filter=Q(status='present'))
            )
            
            total_classes = attendance_stats['total'] or 0
            present_classes = attendance_stats['present'] or 0
            attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
            
            recent_records = Attendance.objects.filter(student=student).select_related('faculty', 'course').order_by('-class_date')[:10]
            
            context = {
                'total_students': 1,
                'total_attendance': total_classes,
                'avg_attendance': round(attendance_percentage, 1),
                'low_attendance_count': 1 if attendance_percentage < 75 else 0,
                'recent_records': recent_records,
                'registered_faces_count': 1 if StudentFace.objects.filter(student=student).exists() else 0,
                'is_student': True,
                'student': student,
            }
        except Student.DoesNotExist:
            context = {
                'total_students': 0,
                'total_attendance': 0,
                'avg_attendance': 0,
                'low_attendance_count': 0,
                'recent_records': [],
                'registered_faces_count': 0,
                'is_student': True,
                'student': None,
            }
    else:
        # OPTIMIZED: Single database query with aggregation
        student_stats = Student.objects.annotate(
            total_classes=Count('attendance'),
            present_classes=Count('attendance', filter=Q(attendance__status='present')),
            attendance_percentage=ExpressionWrapper(
                Case(
                    When(total_classes=0, then=0.0),
                    default=100.0 * F('present_classes') / F('total_classes')
                ),
                output_field=FloatField()
            )
        ).aggregate(
            total_students=Count('id'),
            avg_attendance=Avg('attendance_percentage'),
            low_attendance=Count('id', filter=Q(attendance_percentage__lt=75.0))
        )
        
        context = {
            'total_students': student_stats['total_students'] or 0,
            'total_attendance': Attendance.objects.count(),
            'avg_attendance': round(student_stats['avg_attendance'] or 0, 1),
            'low_attendance_count': student_stats['low_attendance'] or 0,
            'recent_records': Attendance.objects.select_related('student', 'faculty', 'course').order_by('-class_date')[:10],
            'registered_faces_count': StudentFace.objects.count(),
            'is_student': False,
        }
    
    return render(request, 'attendance/attendance_home.html', context)

@login_required
@faculty_required
def add_student(request):
    """Add student - faculty only"""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student details added successfully!')
            return redirect('attendance:attendance_home')
    else:
        form = StudentForm()
    return render(request, 'attendance/add_student.html', {'form': form})

@login_required
@faculty_required
def mark_attendance(request):
    """Mark attendance for all students in bulk - faculty only"""
    # Get the logged-in faculty member
    try:
        faculty = CampusFaculty.objects.get(user=request.user)
    except CampusFaculty.DoesNotExist:
        messages.error(request, 'Faculty profile not found. Please contact administrator.')
        return redirect('attendance:attendance_home')
    
    # Get only courses assigned to this faculty
    my_courses = Course.objects.filter(assigned_faculty=faculty).order_by('name')
    
    if request.method == 'POST':
        course_id = request.POST.get('course')
        class_date = request.POST.get('class_date')
        class_time = request.POST.get('class_time')
        mode = request.POST.get('mode', 'manual')
        
        if not course_id or not class_date or not class_time:
            messages.error(request, 'Please fill in all required fields (Course, Date, and Time).')
            return redirect('attendance:mark_attendance')
        
        try:
            course = Course.objects.get(id=course_id, assigned_faculty=faculty)
        except Course.DoesNotExist:
            messages.error(request, 'You are not authorized to mark attendance for this course.')
            return redirect('attendance:mark_attendance')
        
        # Get all students
        all_students = Student.objects.all().order_by('name')
        
        marked_count = 0
        updated_count = 0
        
        for student in all_students:
            student_status = request.POST.get(f'status_{student.id}')
            
            if student_status in ['present', 'absent']:
                # Update or create attendance record
                attendance, created = Attendance.objects.update_or_create(
                    student=student,
                    faculty=faculty,
                    course=course,
                    class_date=class_date,
                    class_time=class_time,
                    defaults={
                        'status': student_status,
                        'mode': mode
                    }
                )
                
                if created:
                    marked_count += 1
                else:
                    updated_count += 1
        
        if marked_count > 0 or updated_count > 0:
            message = f'Attendance marked successfully! '
            if marked_count > 0:
                message += f'{marked_count} new record(s) created. '
            if updated_count > 0:
                message += f'{updated_count} record(s) updated.'
            messages.success(request, message)
        else:
            messages.warning(request, 'No attendance was marked. Please select at least one student.')
        
        return redirect('attendance:attendance_summary')
    
    # GET request - show the form
    all_students = Student.objects.all().order_by('name')
    faculties = CampusFaculty.objects.all()
    
    # Get current date and time for defaults
    from datetime import datetime
    current_date = datetime.now().date()
    current_time = datetime.now().strftime('%H:00')  # Round to current hour
    
    return render(request, 'attendance/mark_attendance.html', {
        'my_courses': my_courses,
        'all_students': all_students,
        'faculties': faculties,
        'courses': my_courses,  # For face recognition mode
        'current_faculty': faculty,
        'current_date': current_date,
        'current_time': current_time,
    })

@login_required
def attendance_summary(request):
    """View attendance summary - OPTIMIZED with database aggregation"""
    LOW_ATTENDANCE_THRESHOLD = 0.75
    
    if request.user.role == 'student':
        try:
            student = Student.objects.get(email=request.user.email)
            
            # Single query with aggregation
            stats = Attendance.objects.filter(student=student).aggregate(
                total=Count('id'),
                present=Count('id', filter=Q(status='present'))
            )
            
            total_classes = stats['total'] or 0
            present_classes = stats['present'] or 0
            attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
            is_risky = attendance_percentage < (LOW_ATTENDANCE_THRESHOLD * 100)

            students_summary = [{
                'student': student,
                'total_classes': total_classes,
                'present_classes': present_classes,
                'attendance_percentage': f'{attendance_percentage:.2f}%',
                'is_risky': is_risky,
            }]
        except Student.DoesNotExist:
            students_summary = []
    else:
        # OPTIMIZED: Single query with annotations instead of loop
        students = Student.objects.annotate(
            total_classes=Count('attendance'),
            present_classes=Count('attendance', filter=Q(attendance__status='present'))
        ).filter(total_classes__gt=0)
        
        students_summary = []
        for student in students:
            attendance_percentage = (student.present_classes / student.total_classes * 100) if student.total_classes > 0 else 0
            is_risky = attendance_percentage < (LOW_ATTENDANCE_THRESHOLD * 100)

            students_summary.append({
                'student': student,
                'total_classes': student.total_classes,
                'present_classes': student.present_classes,
                'attendance_percentage': f'{attendance_percentage:.2f}%',
                'is_risky': is_risky,
            })
    
    return render(request, 'attendance/attendance_summary.html', {'students_summary': students_summary})

@login_required
@faculty_required
def register_face(request, student_id=None):
    """Register student face for AI attendance - faculty only - OPTIMIZED"""
    selected_student = None
    
    if student_id:
        selected_student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_object_or_404(Student, id=student_id)
        
        temp_path = None
        
        try:
            captured_image_data = request.POST.get('captured_image')
            
            if captured_image_data:
                import base64
                from io import BytesIO
                from PIL import Image
                
                if 'base64,' in captured_image_data:
                    captured_image_data = captured_image_data.split('base64,')[1]
                
                image_data = base64.b64decode(captured_image_data)
                image = Image.open(BytesIO(image_data))
                
                temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', f'captured_{student_id}.jpg')
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                image.save(temp_path, 'JPEG')
                
            elif 'face_image' in request.FILES:
                face_image = request.FILES['face_image']
                temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', face_image.name)
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                
                with open(temp_path, 'wb+') as destination:
                    for chunk in face_image.chunks():
                        destination.write(chunk)
            else:
                messages.error(request, 'Please capture a photo or upload a face image.')
                return redirect('attendance:register_face')
            
            # process_and_encode_face now accepts a file path when called from here
            # We use encode_face_from_image directly since we already have the path
            from .face_recognition_utils import encode_face_from_image
            success, message, face_encoding, quality_score = encode_face_from_image(temp_path)
            
            # Clean up temp file
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            
            if not success:
                messages.error(request, message)
                return redirect('attendance:register_face')
            
            # Save face encoding to database
            student_face, created = StudentFace.objects.update_or_create(
                student=student,
                defaults={'face_encoding': pickle.dumps(face_encoding)}
            )
            
            if created:
                messages.success(request, f'Face registered successfully for {student.name}!')
            else:
                messages.success(request, f'Face updated successfully for {student.name}!')
            
            return redirect('attendance:student_list')
            
        except Exception as e:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            messages.error(request, f'Error processing image: {str(e)}')
            return redirect('attendance:register_face')
    
    students = Student.objects.annotate(
        has_face=Count('studentface')
    ).only('id', 'name', 'student_id', 'email').order_by('name')
    
    return render(request, 'attendance/register_face.html', {
        'students': students,
        'selected_student': selected_student
    })

@login_required
@faculty_required
def start_face_attendance(request):
    """Start face recognition attendance system - faculty only"""
    faculties = CampusFaculty.objects.all()
    courses = Course.objects.all()
    
    # Get pre-selected values from URL parameters
    selected_faculty_id = request.GET.get('faculty_id')
    selected_course_id = request.GET.get('course_id')
    
    return render(request, 'attendance/start_face_attendance.html', {
        'faculties': faculties,
        'courses': courses,
        'selected_faculty_id': selected_faculty_id,
        'selected_course_id': selected_course_id,
    })

@login_required
def video_feed(request):
    """Video streaming route for face recognition - accessible to all authenticated users"""
    # load_known_faces() now returns an int count; calling it here just pre-loads the cache
    load_known_faces()

    return StreamingHttpResponse(
        generate_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

@csrf_exempt
@login_required
@faculty_required
def capture_attendance(request):
    """
    Accepts a base64-encoded JPEG frame from the browser webcam,
    runs face recognition on it, marks attendance, and returns JSON.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required', 'success': False}, status=405)

    try:
        data      = json.loads(request.body)
        faculty_id = data.get('faculty_id')
        course_id  = data.get('course_id')
        frame_b64  = data.get('frame')          # base64-encoded JPEG from browser

        if not faculty_id:
            return JsonResponse({'error': 'Faculty is required', 'success': False}, status=400)

        faculty = get_object_or_404(CampusFaculty, id=faculty_id)
        course  = get_object_or_404(Course, id=course_id) if course_id else None

        # ── Load known faces ──────────────────────────────────────────────────
        face_count = load_known_faces()
        if face_count == 0:
            return JsonResponse({
                'success': False,
                'error': 'No registered faces found. Please register student faces first.'
            }, status=400)

        # ── Decode the browser frame ──────────────────────────────────────────
        if not frame_b64:
            return JsonResponse({'success': False, 'error': 'No frame data received.'}, status=400)

        if ',' in frame_b64:
            frame_b64 = frame_b64.split(',', 1)[1]

        img_bytes = base64.b64decode(frame_b64)
        nparr     = np.frombuffer(img_bytes, np.uint8)
        frame     = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return JsonResponse({'success': False, 'error': 'Could not decode image frame.'}, status=400)

        # ── Detect + recognise faces ──────────────────────────────────────────
        boxes = _detect_faces_opencv(frame)
        if not boxes:
            return JsonResponse({
                'success': True,
                'recognized': False,
                'marked_students': [],
                'count': 0,
                'message': 'No face detected in frame. Please face the camera.'
            })

        matched = {}   # student_id -> (name, confidence)
        for box in boxes:
            embedding = _embed_cropped_face(frame, box)
            if embedding is None:
                continue
            name, sid, conf = _find_best_match(embedding)
            if sid and sid not in matched:
                matched[sid] = (name, conf)

        if not matched:
            return JsonResponse({
                'success': True,
                'recognized': False,
                'marked_students': [],
                'count': 0,
                'message': 'Face detected but not recognized. Ensure face is registered.'
            })

        # ── Mark attendance ───────────────────────────────────────────────────
        now        = datetime.now()
        class_date = now.date()
        class_time = now.time().replace(second=0, microsecond=0)

        recognized_list = [(sid, conf) for sid, (name, conf) in matched.items()]
        marked_count, student_details = mark_attendance_for_recognized_faces(
            recognized_list, faculty, course, class_date, class_time
        )

        # Build response list with already-marked flag
        marked_students = []
        for name, conf, already_marked in student_details:
            marked_students.append({
                'name':          name,
                'confidence':    round(conf * 100, 1),
                'already_marked': already_marked,
            })

        return JsonResponse({
            'success':         True,
            'recognized':      True,
            'marked_students': marked_students,
            'count':           len(marked_students),
            'new_count':       marked_count,
            'message':         f'Attendance marked for {len(marked_students)} student(s).'
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def absentee_alerts(request):
    """View absentee alerts - OPTIMIZED with database aggregation"""
    LOW_ATTENDANCE_THRESHOLD = 0.75
    low_attendance_students = []
    
    if request.user.role == 'student':
        try:
            student = Student.objects.get(email=request.user.email)
            
            # Single query with aggregation
            stats = Attendance.objects.filter(student=student).aggregate(
                total=Count('id'),
                present=Count('id', filter=Q(status='present'))
            )
            
            total_classes = stats['total'] or 0
            present_classes = stats['present'] or 0
            
            if total_classes > 0:
                attendance_percentage = (present_classes / total_classes) * 100
                
                if attendance_percentage < (LOW_ATTENDANCE_THRESHOLD * 100):
                    low_attendance_students.append({
                        'student': student,
                        'total_classes': total_classes,
                        'present_classes': present_classes,
                        'attendance_percentage': round(attendance_percentage, 2),
                        'classes_needed': int((LOW_ATTENDANCE_THRESHOLD * total_classes) - present_classes) + 1
                    })
        except Student.DoesNotExist:
            pass
    else:
        # OPTIMIZED: Single query with annotations and filtering
        students = Student.objects.annotate(
            total_classes=Count('attendance'),
            present_classes=Count('attendance', filter=Q(attendance__status='present')),
            attendance_percentage=ExpressionWrapper(
                Case(
                    When(total_classes=0, then=0.0),
                    default=100.0 * F('present_classes') / F('total_classes')
                ),
                output_field=FloatField()
            )
        ).filter(
            total_classes__gt=0,
            attendance_percentage__lt=(LOW_ATTENDANCE_THRESHOLD * 100)
        )
        
        for student in students:
            low_attendance_students.append({
                'student': student,
                'total_classes': student.total_classes,
                'present_classes': student.present_classes,
                'attendance_percentage': round(student.attendance_percentage, 2),
                'classes_needed': int((LOW_ATTENDANCE_THRESHOLD * student.total_classes) - student.present_classes) + 1
            })
    
    return render(request, 'attendance/absentee_alerts.html', {'low_attendance_students': low_attendance_students})

@login_required
def student_list(request):
    """View student list - OPTIMIZED with prefetch and annotations"""
    # OPTIMIZED: Use annotation to check for faces in a single query
    # Note: StudentFace uses OneToOneField, so the reverse relation is 'studentface' not 'studentface_set'
    students = Student.objects.annotate(
        has_face=Count('studentface')
    ).select_related('studentface')  # Changed from prefetch_related to select_related for OneToOne
    
    students_with_faces = [
        {
            'student': student,
            'has_face': student.has_face > 0
        }
        for student in students
    ]
    
    context = {
        'students_with_faces': students_with_faces,
        'is_faculty': request.user.role in ['faculty', 'admin']
    }
    
    return render(request, 'attendance/student_list.html', context)

@login_required
@faculty_required
def delete_student(request, student_id):
    """Delete a student - faculty only"""
    if request.method == 'POST':
        student = get_object_or_404(Student, id=student_id)
        student_name = student.name
        student.delete()
        messages.success(request, f'Student {student_name} deleted successfully!')
    return redirect('attendance:student_list')

@login_required
@faculty_required
def delete_face(request, student_id):
    """Delete registered face for a student - faculty only"""
    if request.method == 'POST':
        student = get_object_or_404(Student, id=student_id)
        try:
            student_face = StudentFace.objects.get(student=student)
            student_face.delete()
            messages.success(request, f'Face deleted for {student.name}')
        except StudentFace.DoesNotExist:
            messages.error(request, 'No registered face found for this student')
    return redirect('attendance:student_list')

@login_required
def attendance_records(request):
    """View detailed attendance records with mode filtering"""
    if request.user.role == 'student':
        try:
            student = Student.objects.get(email=request.user.email)
            records = Attendance.objects.filter(student=student).select_related(
                'faculty', 'course'
            ).order_by('-class_date', '-class_time')
        except Student.DoesNotExist:
            records = []
    else:
        records = Attendance.objects.select_related(
            'student', 'faculty', 'course'
        ).order_by('-class_date', '-class_time')
    
    # Get filter parameters
    mode_filter = request.GET.get('mode', 'all')
    status_filter = request.GET.get('status', 'all')
    
    # Apply filters
    if mode_filter != 'all':
        records = records.filter(mode=mode_filter)
    if status_filter != 'all':
        records = records.filter(status=status_filter)
    
    # Get statistics
    total_records = records.count()
    ai_records = records.filter(mode='AI').count()
    manual_records = records.filter(mode='manual').count()
    remedial_records = records.filter(mode='remedial').count()
    
    context = {
        'records': records[:100],  # Limit to 100 most recent
        'total_records': total_records,
        'ai_records': ai_records,
        'manual_records': manual_records,
        'remedial_records': remedial_records,
        'mode_filter': mode_filter,
        'status_filter': status_filter,
        'is_student': request.user.role == 'student',
    }
    
    return render(request, 'attendance/attendance_records.html', context)

@login_required
@faculty_required
def faculty_attendance_history(request):
    """View attendance history for the logged-in faculty member"""
    try:
        faculty = CampusFaculty.objects.get(user=request.user)
    except CampusFaculty.DoesNotExist:
        messages.error(request, 'Faculty profile not found. Please contact administrator.')
        return redirect('attendance:attendance_home')
    
    # Get all attendance records marked by this faculty
    records = Attendance.objects.filter(faculty=faculty).select_related(
        'student', 'course'
    ).order_by('-class_date', '-class_time')
    
    # Get filter parameters
    mode_filter = request.GET.get('mode', 'all')
    status_filter = request.GET.get('status', 'all')
    course_filter = request.GET.get('course', 'all')
    
    # Apply filters
    if mode_filter != 'all':
        records = records.filter(mode=mode_filter)
    if status_filter != 'all':
        records = records.filter(status=status_filter)
    if course_filter != 'all':
        records = records.filter(course_id=course_filter)
    
    # Get statistics
    total_records = records.count()
    ai_records = records.filter(mode='AI').count()
    manual_records = records.filter(mode='manual').count()
    remedial_records = records.filter(mode='remedial').count()
    present_count = records.filter(status='present').count()
    absent_count = records.filter(status='absent').count()
    
    # Get courses for filter dropdown
    my_courses = Course.objects.filter(assigned_faculty=faculty).order_by('name')
    
    context = {
        'records': records[:100],  # Limit to 100 most recent
        'total_records': total_records,
        'ai_records': ai_records,
        'manual_records': manual_records,
        'remedial_records': remedial_records,
        'present_count': present_count,
        'absent_count': absent_count,
        'mode_filter': mode_filter,
        'status_filter': status_filter,
        'course_filter': course_filter,
        'my_courses': my_courses,
        'faculty': faculty,
    }
    
    return render(request, 'attendance/faculty_attendance_history.html', context)
