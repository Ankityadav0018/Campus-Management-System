import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from werkzeug.utils import secure_filename
import os
import numpy as np

# Import face recognition utilities
from face_recognition_utils import load_known_faces, process_and_encode_face, generate_frames

app = Flask(__name__)
app.secret_key = 'e45d76fe337a60b9320e95c0c944316d466cd958a728081267cb6b03d3b7c060' # Replace with a strong secret key in production
app.config['UPLOAD_FOLDER'] = './uploads' # Directory to save uploaded images temporary

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        with open('init_db.sql', 'r') as f:
            db.executescript(f.read())
        db.commit()

@app.route('/')
def index():
    db = get_db()
    # Fetch student data by joining users and students table
    students = db.execute('''SELECT u.id AS user_id, u.name, u.email, s.student_id, s.course, s.block, s.parent_contact
                           FROM users u LEFT JOIN students s ON u.id = s.user_id WHERE u.role = "student"''').fetchall()
    db.close()
    return render_template('index.html', students=students)

@app.route('/register_user', methods=('GET', 'POST'))
def register_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        if not name or not email or not password or not role:
            flash('All fields are required!')
        else:
            try:
                db = get_db()
                cursor = db.execute('INSERT INTO users (name, role, email, password) VALUES (?, ?, ?, ?)',
                                   (name, role, email, password))
                user_id = cursor.lastrowid
                db.commit()
                db.close()
                flash(f'User registered successfully! Now add {role} details.')
                if role == 'student':
                    return redirect(url_for('add_student_details_for_user', user_id=user_id))
                elif role == 'faculty':
                    return redirect(url_for('add_faculty_details_for_user', user_id=user_id))
            except sqlite3.IntegrityError:
                flash('Email already registered!')
                
    return render_template('register_user.html')

@app.route('/add_student_details_for_user/<int:user_id>', methods=('GET', 'POST'))
def add_student_details_for_user(user_id):
    db = get_db()
    user = db.execute('SELECT id, name, email FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        flash('User not found!')
        return redirect(url_for('register_user'))

    if request.method == 'POST':
        course = request.form['course']
        block = request.form['block']
        parent_contact = request.form['parent_contact']

        if not course or not block or not parent_contact:
            flash('All fields are required!')
        else:
            try:
                db.execute('INSERT INTO students (user_id, course, block, parent_contact) VALUES (?, ?, ?, ?)',
                           (user_id, course, block, parent_contact))
                db.commit()
                flash('Student details added successfully!')
                return redirect(url_for('students_list'))
            except sqlite3.IntegrityError:
                flash('Student details for this user already exist!')
            finally:
                db.close()

    db.close()
    return render_template('add_student_details_for_user.html', user=user)

@app.route('/faculty_list')
def faculty_list():
    db = get_db()
    faculty_members = db.execute('''SELECT u.id AS user_id, u.name, u.email, f.faculty_id, f.department
                                  FROM users u JOIN faculty f ON u.id = f.user_id WHERE u.role = "faculty"''').fetchall()
    db.close()
    return render_template('faculty_list.html', faculty_members=faculty_members)

@app.route('/add_faculty_details_for_user/<int:user_id>', methods=('GET', 'POST'))
def add_faculty_details_for_user(user_id):
    db = get_db()
    user = db.execute('SELECT id, name, email FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        flash('User not found!')
        return redirect(url_for('register_user'))

    if request.method == 'POST':
        department = request.form['department']

        if not department:
            flash('Department is required!')
        else:
            try:
                db.execute('INSERT INTO faculty (user_id, department) VALUES (?, ?)',
                           (user_id, department))
                db.commit()
                flash('Faculty details added successfully!')
                return redirect(url_for('faculty_list'))
            except sqlite3.IntegrityError:
                flash('Faculty details for this user already exist!')
            finally:
                db.close()
    
    db.close()
    return render_template('add_faculty_details_for_user.html', user=user)

@app.route('/edit_faculty_details/<int:faculty_id>', methods=('GET', 'POST'))
def edit_faculty_details(faculty_id):
    db = get_db()
    faculty_member = db.execute('''SELECT u.id AS user_id, u.name, u.email, f.faculty_id, f.department
                                 FROM users u JOIN faculty f ON u.id = f.user_id WHERE f.faculty_id = ?''', (faculty_id,)).fetchone()
    
    if faculty_member is None:
        flash('Faculty member not found!')
        return redirect(url_for('faculty_list'))

    if request.method == 'POST':
        department = request.form['department']

        if not department:
            flash('Department is required!')
        else:
            db.execute('UPDATE faculty SET department = ? WHERE faculty_id = ?',
                       (department, faculty_id))
            db.commit()
            flash('Faculty details updated successfully!')
            return redirect(url_for('faculty_list'))
    
    db.close()
    return render_template('edit_faculty_details.html', faculty_member=faculty_member)

@app.route('/delete_faculty_details/<int:faculty_id>', methods=('POST',))
def delete_faculty_details(faculty_id):
    db = get_db()
    db.execute('DELETE FROM faculty WHERE faculty_id = ?', (faculty_id,))
    db.commit()
    db.close()
    flash('Faculty details deleted successfully!')
    return redirect(url_for('faculty_list'))

@app.route('/classrooms')
def classrooms():
    db = get_db()
    classrooms = db.execute('SELECT * FROM classrooms').fetchall()
    db.close()
    return render_template('classrooms.html', classrooms=classrooms)

@app.route('/add_classroom', methods=('GET', 'POST'))
def add_classroom():
    if request.method == 'POST':
        name = request.form['name']
        capacity = request.form['capacity']

        if not name or not capacity:
            flash('All fields are required!')
        else:
            try:
                db = get_db()
                db.execute('INSERT INTO classrooms (name, capacity) VALUES (?, ?)',
                           (name, capacity))
                db.commit()
                db.close()
                flash('Classroom added successfully!')
                return redirect(url_for('classrooms'))
            except sqlite3.IntegrityError:
                flash('Classroom name already exists!')
    return render_template('add_classroom.html')

@app.route('/edit_classroom/<int:classroom_id>', methods=('GET', 'POST'))
def edit_classroom(classroom_id):
    db = get_db()
    classroom = db.execute('SELECT * FROM classrooms WHERE id = ?', (classroom_id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        capacity = request.form['capacity']

        if not name or not capacity:
            flash('All fields are required!')
        else:
            try:
                db.execute('UPDATE classrooms SET name = ?, capacity = ? WHERE id = ?',
                           (name, capacity, classroom_id))
                db.commit()
                db.close()
                flash('Classroom updated successfully!')
                return redirect(url_for('classrooms'))
            except sqlite3.IntegrityError:
                flash('Classroom name already exists!')
    db.close()
    return render_template('edit_classroom.html', classroom=classroom)

@app.route('/delete_classroom/<int:classroom_id>', methods=('POST',))
def delete_classroom(classroom_id):
    db = get_db()
    db.execute('DELETE FROM classrooms WHERE id = ?', (classroom_id,))
    db.commit()
    db.close()
    flash('Classroom deleted successfully!')
    return redirect(url_for('classrooms'))

@app.route('/schedules')
def schedules():
    db = get_db()
    schedules = db.execute('''SELECT s.id, c.name AS classroom_name, s.day_of_week, s.start_time, s.end_time, s.course_name, u.name AS faculty_name 
                           FROM schedules s 
                           JOIN classrooms c ON s.classroom_id = c.id 
                           LEFT JOIN faculty f ON s.faculty_id = f.faculty_id
                           LEFT JOIN users u ON f.user_id = u.id''').fetchall()
    db.close()
    return render_template('schedules.html', schedules=schedules)

@app.route('/add_schedule', methods=('GET', 'POST'))
def add_schedule():
    db = get_db()
    classrooms = db.execute('SELECT id, name FROM classrooms').fetchall()
    faculty = db.execute('SELECT f.faculty_id, u.name FROM faculty f JOIN users u ON f.user_id = u.id').fetchall()

    if request.method == 'POST':
        classroom_id = request.form['classroom_id']
        day_of_week = request.form['day_of_week']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        course_name = request.form['course_name']
        faculty_id = request.form['faculty_id'] if request.form['faculty_id'] else None

        if not classroom_id or not day_of_week or not start_time or not end_time:
            flash('Required fields: Classroom, Day, Start Time, End Time')
        else:
            try:
                db.execute('INSERT INTO schedules (classroom_id, day_of_week, start_time, end_time, course_name, faculty_id) VALUES (?, ?, ?, ?, ?, ?)',
                           (classroom_id, day_of_week, start_time, end_time, course_name, faculty_id))
                db.commit()
                flash('Schedule entry added successfully!')
                return redirect(url_for('schedules'))
            except sqlite3.IntegrityError as e:
                flash(f'Error adding schedule: {e}')
            finally:
                db.close()
    
    db.close()
    return render_template('add_schedule.html', classrooms=classrooms, faculty=faculty)

@app.route('/view_classroom_schedule/<int:classroom_id>')
def view_classroom_schedule(classroom_id):
    db = get_db()
    classroom = db.execute('SELECT * FROM classrooms WHERE id = ?', (classroom_id,)).fetchone()
    schedules = db.execute('''SELECT s.id, c.name AS classroom_name, s.day_of_week, s.start_time, s.end_time, s.course_name, u.name AS faculty_name 
                           FROM schedules s 
                           JOIN classrooms c ON s.classroom_id = c.id 
                           LEFT JOIN faculty f ON s.faculty_id = f.faculty_id
                           LEFT JOIN users u ON f.user_id = u.id 
                           WHERE s.classroom_id = ? ORDER BY s.day_of_week, s.start_time''', (classroom_id,)).fetchall()
    db.close()
    return render_template('classroom_schedule.html', classroom=classroom, schedules=schedules)

@app.route('/attendance')
def attendance():
    db = get_db()
    attendance_records = db.execute('''SELECT a.id, u.name AS student_name, a.date, a.status 
                                   FROM attendance a 
                                   JOIN students s ON a.student_id = s.student_id
                                   JOIN users u ON s.user_id = u.id
                                   ORDER BY a.date DESC, u.name''').fetchall()
    db.close()
    return render_template('attendance.html', attendance_records=attendance_records)

@app.route('/mark_attendance', methods=('GET', 'POST'))
def mark_attendance():
    db = get_db()
    students = db.execute('SELECT s.student_id, u.name FROM students s JOIN users u ON s.user_id = u.id').fetchall()

    if request.method == 'POST':
        student_id = request.form['student_id']
        date = request.form['date']
        status = request.form['status']

        if not student_id or not date or not status:
            flash('All fields are required!')
        else:
            try:
                db.execute('INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)',
                           (student_id, date, status))
                db.commit()
                flash('Attendance marked successfully!')
                return redirect(url_for('attendance'))
            except sqlite3.IntegrityError as e:
                flash(f'Error marking attendance: {e}')
            finally:
                db.close()
    
    db.close()
    return render_template('mark_attendance.html', students=students)

def get_risky_students(attendance_threshold=0.75):
    db = get_db()
    # Get total unique days attendance was taken
    total_days_query = db.execute('SELECT COUNT(DISTINCT date) FROM attendance').fetchone()[0]
    
    if total_days_query == 0:
        db.close()
        return []

    # Calculate attendance percentage for each student
    risky_students_query = db.execute('''
        SELECT 
            s.student_id,
            u.name,
            CAST(SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS REAL) * 100 / ? AS attendance_percentage
        FROM students s
        JOIN users u ON s.user_id = u.id
        LEFT JOIN attendance a ON s.student_id = a.student_id
        GROUP BY s.student_id, u.name
        HAVING attendance_percentage < ?
        ORDER BY attendance_percentage ASC
    ''', (total_days_query, attendance_threshold * 100)).fetchall()
    
    db.close()
    return risky_students_query

@app.route('/absentee_alerts')
def absentee_alerts():
    risky_students = get_risky_students()
    return render_template('absentee_alerts.html', risky_students=risky_students)

@app.route('/students')
def students_list():
    db = get_db()
    # Join users and students table to get comprehensive student details
    students = db.execute('''SELECT u.id AS user_id, u.name, u.email, s.student_id, s.course, s.block, s.parent_contact
                           FROM users u JOIN students s ON u.id = s.user_id WHERE u.role = "student"''').fetchall()
    db.close()
    return render_template('students_list.html', students=students)

@app.route('/register_face/<int:student_id>', methods=['GET', 'POST'])
def register_face(student_id):
    db = get_db()
    student_name = db.execute('SELECT u.name FROM students s JOIN users u ON s.user_id = u.id WHERE s.student_id = ?', (student_id,)).fetchone()
    db.close()

    if student_name is None:
        flash("Student not found.")
        return redirect(url_for('students_list'))
    student_name = student_name['name']

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            face_encoding, error = process_and_encode_face(filepath)
            os.remove(filepath) # Clean up the uploaded file

            if error:
                flash(f'Error: {error}')
            elif face_encoding is not None:
                db = get_db()
                # Store face_encoding as BLOB (numpy array converted to bytes)
                db.execute('INSERT INTO student_faces (student_id, face_encoding) VALUES (?, ?)',
                           (student_id, face_encoding.tobytes()))
                db.commit()
                db.close()
                flash('Face registered successfully!')
                return redirect(url_for('students_list'))
            
    return render_template('register_face.html', student_id=student_id, student_name=student_name)

@app.route('/start_face_attendance')
def start_face_attendance():
    return render_template('start_face_attendance.html')

@app.route('/video_feed')
def video_feed():
    known_face_encodings, known_face_names, known_student_ids = load_known_faces()
    return Response(generate_frames(known_face_encodings, known_face_names, known_student_ids), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/edit_student_details/<int:student_id>', methods=('GET', 'POST'))
def edit_student_details(student_id):
    db = get_db()
    student = db.execute('''SELECT u.id AS user_id, u.name, u.email, s.student_id, s.course, s.block, s.parent_contact
                           FROM users u JOIN students s ON u.id = s.user_id WHERE s.student_id = ?''', (student_id,)).fetchone()
    
    if student is None:
        flash('Student not found!')
        return redirect(url_for('students_list'))

    if request.method == 'POST':
        course = request.form['course']
        block = request.form['block']
        parent_contact = request.form['parent_contact']

        if not course or not block or not parent_contact:
            flash('All fields are required!')
        else:
            db.execute('UPDATE students SET course = ?, block = ?, parent_contact = ? WHERE student_id = ?',
                       (course, block, parent_contact, student_id))
            db.commit()
            flash('Student details updated successfully!')
            return redirect(url_for('students_list'))
    
    db.close()
    return render_template('edit_student_details.html', student=student)

@app.route('/delete_student_details/<int:student_id>', methods=('POST',))
def delete_student_details(student_id):
    db = get_db()
    db.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
    db.commit()
    db.close()
    flash('Student details deleted successfully!')
    return redirect(url_for('students_list'))


if __name__ == '__main__':
    # Ensure the uploads directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    init_db()
    app.run(debug=True)