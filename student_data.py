import json
import os

DATA_FILE = 'students.json'

DEFAULT_STUDENTS = {
    'STU001': {
        'id': 'STU001',
        'name': 'Rahul Kumar',
        'password': 'rahul123',
        'email': 'rahul@example.com',
        'phone': '+91 9876543210',
        'class': 'Class 10',
        'enrollment_date': '2024-01-15',
        'marks': {'Mathematics': 85, 'Science': 78, 'Physics': 82, 'Chemistry': 75},
        'attendance': {'total_classes': 40, 'attended': 38, 'percentage': 95.0},
        'progress': {'completion': 75, 'status': 'On Track', 'performance': 'Good'}
    }
}

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_STUDENTS)
        return DEFAULT_STUDENTS
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def authenticate_student(student_id, password):
    students = load_data()
    student = students.get(student_id)
    if student and student['password'] == password:
        data = student.copy()
        data.pop('password', None)
        return data
    return None

def get_student(student_id):
    students = load_data()
    student = students.get(student_id)
    if student:
        data = student.copy()
        data.pop('password', None)
        return data
    return None

def update_student(student_id, data):
    students = load_data()
    if student_id in students:
        # Preserve password if not provided
        if 'password' not in data:
            data['password'] = students[student_id]['password']
        students[student_id] = data
        save_data(students)
        return True
    return False

def add_student(student_data):
    students = load_data()
    students[student_data['id']] = student_data
    save_data(students)
    return True

def delete_student(student_id):
    students = load_data()
    if student_id in students:
        del students[student_id]
        save_data(students)
        return True
    return False

def get_all_students():
    students = load_data()
    return [{**v, 'id': k} for k, v in students.items()]
