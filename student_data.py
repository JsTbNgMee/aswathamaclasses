from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    student_class = db.Column(db.String(50))
    enrollment_date = db.Column(db.String(20))
    
    # Storing complex data as JSON strings for simplicity in this specific project
    tests_json = db.Column(db.Text, default='[]')
    attendance_log_json = db.Column(db.Text, default='[]')
    progress_json = db.Column(db.Text, default='{"completion": 0, "status": "New", "performance": "N/A"}')

    @property
    def tests(self):
        return json.loads(self.tests_json)
    
    @tests.setter
    def tests(self, value):
        self.tests_json = json.dumps(value)

    @property
    def attendance_log(self):
        return json.loads(self.attendance_log_json)
    
    @attendance_log.setter
    def attendance_log(self, value):
        self.attendance_log_json = json.dumps(value)

    @property
    def progress(self):
        return json.loads(self.progress_json)
    
    @progress.setter
    def progress(self, value):
        self.progress_json = json.dumps(value)

    @property
    def attendance(self):
        log = self.attendance_log
        total = len(log)
        present = sum(1 for entry in log if entry.get('status') == 'Present')
        return {
            'total_classes': total,
            'attended': present,
            'percentage': (present / total * 100) if total > 0 else 0
        }

def init_db(app):
    db.init_app(app)
    with app.app_context():
        # Use a more robust check for table existence
        inspector = db.inspect(db.engine)
        if not inspector.has_table("student"):
            db.create_all()
            # Migrate existing JSON data if needed
            if os.path.exists('students.json'):
                with open('students.json', 'r') as f:
                    try:
                        data = json.load(f)
                        for sid, sdata in data.items():
                            if not Student.query.get(sid):
                                student = Student(
                                    id=sid,
                                    name=sdata.get('name'),
                                    password=sdata.get('password'),
                                    email=sdata.get('email'),
                                    phone=sdata.get('phone'),
                                    student_class=sdata.get('class'),
                                    enrollment_date=sdata.get('enrollment_date')
                                )
                                student.tests = sdata.get('tests', [])
                                student.attendance_log = sdata.get('attendance_log', [])
                                student.progress = sdata.get('progress', {})
                                db.session.add(student)
                        db.session.commit()
                    except Exception as e:
                        print(f"Migration error: {e}")

def authenticate_student(student_id, password):
    student = Student.query.get(student_id)
    if student and student.password == password:
        return get_student(student_id)
    return None

def get_student(student_id):
    student = Student.query.get(student_id)
    if student:
        return {
            'id': student.id,
            'name': student.name,
            'email': student.email,
            'phone': student.phone,
            'class': student.student_class,
            'enrollment_date': student.enrollment_date,
            'tests': student.tests,
            'attendance_log': student.attendance_log,
            'attendance': student.attendance,
            'progress': student.progress
        }
    return None

def update_student(student_id, data):
    student = Student.query.get(student_id)
    if student:
        student.name = data.get('name', student.name)
        student.student_class = data.get('class', student.student_class)
        student.email = data.get('email', student.email)
        student.phone = data.get('phone', student.phone)
        student.tests = data.get('tests', student.tests)
        student.attendance_log = data.get('attendance_log', student.attendance_log)
        student.progress = data.get('progress', student.progress)
        if 'password' in data:
            student.password = data['password']
        db.session.commit()
        return True
    return False

def add_student(data):
    student = Student(
        id=data['id'],
        name=data['name'],
        password=data['password'],
        student_class=data.get('class'),
        email=data.get('email', ''),
        phone=data.get('phone', ''),
        enrollment_date=data.get('enrollment_date', datetime.now().strftime('%Y-%m-%d'))
    )
    student.tests = data.get('tests', [])
    student.attendance_log = data.get('attendance_log', [])
    student.progress = data.get('progress', {"completion": 0, "status": "New", "performance": "N/A"})
    db.session.add(student)
    db.session.commit()
    return True

def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
        return True
    return False

def get_all_students():
    students = Student.query.all()
    return [{
        'id': s.id,
        'name': s.name,
        'class': s.student_class,
        'email': s.email,
        'phone': s.phone
    } for s in students]
