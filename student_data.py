import json
import os
from datetime import datetime

DATA_FILE = 'students.json'

DEFAULT_STUDENT = {
    'id': 'STU001',
    'name': 'Rahul Kumar',
    'password': 'rahul123',
    'email': 'rahul@example.com',
    'phone': '+91 9876543210',
    'class': 'Class 10',
    'enrollment_date': '2024-01-15',
    'tests': [
        {'name': 'Week 1 Unit Test', 'date': '2024-01-20', 'marks': 85, 'total': 100},
        {'name': 'Week 2 Quiz', 'date': '2024-01-27', 'marks': 78, 'total': 100}
    ],
    'attendance_log': [
        {'date': '2024-01-15', 'status': 'Present'},
        {'date': '2024-01-16', 'status': 'Present'},
        {'date': '2024-01-17', 'status': 'Absent'}
    ],
    'progress': {'completion': 75, 'status': 'On Track', 'performance': 'Good'}
}

def load_data():
    if not os.path.exists(DATA_FILE):
        data = {'STU001': DEFAULT_STUDENT}
        save_data(data)
        return data
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
