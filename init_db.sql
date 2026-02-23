CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE classrooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    capacity INTEGER
);

CREATE TABLE schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    classroom_id INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    course_name TEXT,
    faculty_id INTEGER,
    FOREIGN KEY (classroom_id) REFERENCES classrooms(id),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
);

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    course TEXT,
    block TEXT,
    parent_contact TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE student_faces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE faculty (
    faculty_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    department TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE food_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_time TEXT NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL
);