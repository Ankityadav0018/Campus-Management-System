# Campus Management System with AI Face Recognition Attendance

A comprehensive Django-based campus management system featuring AI-powered face recognition for automated attendance marking.

## 🚀 Features

### Attendance Management
- **AI Face Recognition**: Automated attendance marking using facial recognition
- **Manual Attendance**: Traditional manual attendance marking option
- **Face Registration**: Easy face registration system for students
- **Attendance Reports**: Comprehensive attendance statistics and summaries
- **Absentee Alerts**: Automatic detection of students with low attendance
- **Real-time Video Feed**: Live camera feed for face recognition

### Other Modules
- Food ordering system
- Resource management
- Remedial class scheduling
- User management (Students, Faculty, Admin)

## 📋 Requirements

- Python 3.8+
- Django 4.2.0
- OpenCV
- face_recognition library
- dlib
- Webcam (for face recognition features)

## 🛠️ Installation

1. **Clone the repository**
```bash
cd /Users/ankityadav/Downloads/project2
```

2. **Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# Or on Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
# Install cmake first (required for dlib)
pip install cmake

# Install all requirements
pip install -r requirements.txt
```

Note: If you face issues installing `dlib` or `face_recognition`, install them separately:
```bash
# For macOS with Homebrew
brew install cmake
pip install dlib
pip install face_recognition
```

4. **Configure Python environment**
Make sure your Python environment is properly configured for the project.

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Create media directories**
```bash
mkdir -p media/temp
```

8. **Run the development server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## 📖 Usage Guide

### Setting Up Face Recognition Attendance

1. **Add Students**
   - Navigate to Attendance → Add Student
   - Fill in student details (ID, Name, Email)
   - Click "Add Student"

2. **Register Student Faces**
   - Go to Attendance → Student List
   - Click "Register Face" button next to a student
   - Upload a clear photo of the student's face
   - Requirements:
     - Good lighting
     - Face clearly visible
     - Only one person in the photo
     - No glasses or face coverings (if possible)

3. **Mark Attendance Using Face Recognition**
   - Navigate to Attendance → Start Face Attendance
   - Select Faculty and Course (optional)
   - Position students in front of the webcam
   - Click "Capture Attendance Now"
   - System will automatically recognize and mark attendance

4. **View Attendance Reports**
   - Go to Attendance → Attendance Summary
   - View detailed statistics for each student
   - Check attendance percentages
   - Identify at-risk students (below 75% attendance)

5. **Check Absentee Alerts**
   - Navigate to Attendance → Absentee Alerts
   - View list of students with low attendance
   - See how many classes needed to reach threshold

## 🏗️ Project Structure

```
project2/
├── apps/
│   ├── attendance/          # Face recognition attendance module
│   │   ├── face_recognition_utils.py  # Face recognition utilities
│   │   ├── models.py        # Student, Attendance, StudentFace models
│   │   ├── views.py         # All attendance views
│   │   ├── urls.py          # URL routing
│   │   └── forms.py         # Forms for attendance
│   ├── users/               # User management
│   ├── food/                # Food ordering
│   ├── resources/           # Resource management
│   └── remedial/            # Remedial classes
├── templates/               # HTML templates
│   └── attendance/
│       ├── register_face.html
│       ├── start_face_attendance.html
│       └── student_list.html
├── static/                  # CSS, JS, images
│   └── css/
│       └── style.css
├── media/                   # User uploads
├── manage.py
└── requirements.txt
```

## 🔧 Configuration

### Settings
Key settings are in `campus_project/settings.py`:
- `MEDIA_ROOT`: Directory for uploaded files
- `MEDIA_URL`: URL prefix for media files
- `AUTH_USER_MODEL`: Custom user model

### Face Recognition Settings
Adjust tolerance in `face_recognition_utils.py`:
```python
matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.6)
```
- Lower tolerance (0.4-0.5): More strict matching
- Higher tolerance (0.6-0.7): More lenient matching

## 🎯 API Endpoints

### Attendance Module
- `/attendance/` - Attendance home
- `/attendance/add-student/` - Add new student
- `/attendance/register-face/` - Register student face
- `/attendance/start-face-attendance/` - Start face recognition
- `/attendance/video-feed/` - Live video stream
- `/attendance/capture-attendance/` - Capture and mark attendance
- `/attendance/summary/` - Attendance summary
- `/attendance/student-list/` - List all students

## 🐛 Troubleshooting

### Face Recognition Not Working
1. Check if webcam is accessible
2. Ensure proper lighting
3. Verify face is registered for students
4. Check browser permissions for camera access

### Installation Issues
- **dlib installation fails**: Install cmake first: `pip install cmake`
- **face_recognition errors**: Ensure dlib is installed correctly
- **OpenCV issues**: Try installing opencv-python-headless

### Database Errors
```bash
# Reset migrations if needed
python manage.py migrate --run-syncdb
```

## 📊 Database Models

### Student Model
- student_id (CharField): Unique identifier
- name (CharField): Full name
- email (EmailField): Email address

### StudentFace Model
- student (OneToOneField): Related student
- face_encoding (BinaryField): Pickled face encoding

### Attendance Model
- student (ForeignKey): Related student
- faculty (ForeignKey): Related faculty
- course (ForeignKey): Related course
- class_date (DateField): Attendance date
- status (CharField): present/absent
- mode (CharField): manual/AI/remedial

## 🔐 Security Notes

- Change `SECRET_KEY` in production
- Use HTTPS in production
- Implement proper authentication
- Secure media file access
- Use environment variables for sensitive data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is for educational purposes.

## 👥 Support

For issues or questions:
1. Check troubleshooting section
2. Review error logs
3. Check Django documentation
4. Review face_recognition library docs

## 🎓 Credits

Built with:
- Django - Web framework
- face_recognition - Face recognition library
- OpenCV - Computer vision
- dlib - Machine learning toolkit
