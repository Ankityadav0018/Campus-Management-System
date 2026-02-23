"""
AI Module views with lazy loading for better performance.
Heavy libraries (cv2, face_recognition) are only imported when needed.
"""
import numpy as np
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import StreamingHttpResponse
from django.utils import timezone
import os

# Django ORM models
from apps.attendance.models import Student, StudentFace, Attendance
from apps.resources.models import CampusFaculty

def ai_home(request):
    """Landing for AI features: Face Recognition, Rush Prediction, Absentee Alert."""
    return render(request, 'ai_module/ai_home.html')

def load_known_faces_from_db():
    known_face_encodings = []
    known_face_names = []
    known_student_ids = []

    faces = StudentFace.objects.all()
    for face_obj in faces:
        known_face_encodings.append(np.frombuffer(face_obj.face_encoding, dtype=np.float64))
        known_face_names.append(face_obj.student.name)
        known_student_ids.append(face_obj.student.student_id)
        
    return known_face_encodings, known_face_names, known_student_ids

def process_and_encode_face(image_path):
    """Process face image - lazy loads face_recognition when called"""
    # Lazy import - only load when needed
    import face_recognition
    
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        return None, "No face found in the image."
    if len(face_locations) > 1:
        return None, "Multiple faces found in the image. Please upload an image with a single face."
    
    face_encoding = face_recognition.face_encodings(image, face_locations)[0]
    return face_encoding, None

def mark_attendance_orm(student_id):
    student = Student.objects.get(student_id=student_id)
    today = timezone.localdate()

    # In a real scenario, you'd likely associate a faculty member or specific course
    # For simplicity, we'll use the first available faculty or a placeholder
    faculty = CampusFaculty.objects.first() # Or retrieve based on context/login

    if not faculty:
        print("Warning: No faculty found to associate with attendance. Please add faculty members.")
        return

    # Check if attendance is already marked for today via AI for this student and faculty
    record = Attendance.objects.filter(student=student, faculty=faculty, class_date=today, mode='AI').first()
    if not record:
        Attendance.objects.create(
            student=student,
            faculty=faculty,
            class_date=today,
            status='present',
            mode='AI'
        )
        print(f"Attendance marked for {student.name} via AI.")

def generate_frames_django():
    """Generate video frames - lazy loads cv2 and face_recognition when called"""
    # Lazy imports - only load when needed
    import cv2
    import face_recognition
    
    known_face_encodings, known_face_names, known_student_ids = load_known_faces_from_db()
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        print("Error: Could not open video stream.")
        return

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            student_id = None

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                student_id = known_student_ids[best_match_index]
                mark_attendance_orm(student_id)

            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\n'
               b'Content-Type: image/jpeg\n\n' + frame + b'\n')

    video_capture.release()
    cv2.destroyAllWindows()


def register_face_view(request, student_id):
    student = Student.objects.filter(student_id=student_id).first()
    if not student:
        messages.error(request, "Student not found.")
        return redirect(reverse('users:student_list')) # Assuming a student list view
    
    if request.method == 'POST':
        if 'file' not in request.FILES:
            messages.error(request, 'No file part')
            return redirect(request.path)
        file = request.FILES['file']
        if file.name == '':
            messages.error(request, 'No selected file')
            return redirect(request.path)
        if file:
            # Ensure the uploads directory exists
            upload_dir = os.path.join(os.getcwd(), 'uploads') # Use os.getcwd() for project root
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            filename = f"student_{student_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            filepath = os.path.join(upload_dir, filename)
            
            with open(filepath, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            face_encoding, error = process_and_encode_face(filepath)
            os.remove(filepath) # Clean up the uploaded file

            if error:
                messages.error(request, f'Error: {error}')
            elif face_encoding is not None:
                # Check if a face already exists for this student
                student_face, created = StudentFace.objects.get_or_create(student=student)
                student_face.face_encoding = face_encoding.tobytes()
                student_face.save()
                messages.success(request, 'Face registered successfully!')
                return redirect(reverse('users:student_list'))
            
    return render(request, 'ai_module/register_face.html', {'student': student})

def start_face_attendance_view(request):
    return render(request, 'ai_module/start_face_attendance.html')

def video_feed_view(request):
    return StreamingHttpResponse(generate_frames_django(), mimetype='multipart/x-mixed-replace; boundary=frame')

def absentee_alert(request):
    """Placeholder for absentee alert AI (links to attendance summary)."""
    return render(request, 'ai_module/absentee_alert.html')
