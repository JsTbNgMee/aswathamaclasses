"""
Student Data Management
Handles student authentication and data without database
Using in-memory storage with sample data
"""

# Sample student data - In production, this could be read from a JSON file
STUDENTS = {
    'STU001': {
        'id': 'STU001',
        'name': 'Rahul Kumar',
        'password': 'rahul123',
        'email': 'rahul@example.com',
        'phone': '+91 9876543210',
        'class': 'Class 10',
        'enrollment_date': '2024-01-15',
        'marks': {
            'Mathematics': 85,
            'Science': 78,
            'Physics': 82,
            'Chemistry': 75
        },
        'attendance': {
            'total_classes': 40,
            'attended': 38,
            'percentage': 95.0
        },
        'progress': {
            'completion': 75,
            'status': 'On Track',
            'performance': 'Good'
        }
    },
    'STU002': {
        'id': 'STU002',
        'name': 'Priya Sharma',
        'password': 'priya123',
        'email': 'priya@example.com',
        'phone': '+91 9876543211',
        'class': 'Class 9',
        'enrollment_date': '2024-02-20',
        'marks': {
            'Mathematics': 92,
            'Science': 88,
            'Physics': 90,
            'Chemistry': 85
        },
        'attendance': {
            'total_classes': 35,
            'attended': 35,
            'percentage': 100.0
        },
        'progress': {
            'completion': 88,
            'status': 'Excellent Progress',
            'performance': 'Excellent'
        }
    },
    'STU003': {
        'id': 'STU003',
        'name': 'Amit Singh',
        'password': 'amit123',
        'email': 'amit@example.com',
        'phone': '+91 9876543212',
        'class': 'Class 8',
        'enrollment_date': '2024-03-10',
        'marks': {
            'Mathematics': 72,
            'Science': 68,
            'Physics': 70,
            'Chemistry': 65
        },
        'attendance': {
            'total_classes': 32,
            'attended': 28,
            'percentage': 87.5
        },
        'progress': {
            'completion': 62,
            'status': 'Needs Improvement',
            'performance': 'Average'
        }
    },
    'STU004': {
        'id': 'STU004',
        'name': 'Neha Patel',
        'password': 'neha123',
        'email': 'neha@example.com',
        'phone': '+91 9876543213',
        'class': 'Class 10',
        'enrollment_date': '2023-12-05',
        'marks': {
            'Mathematics': 88,
            'Science': 85,
            'Physics': 87,
            'Chemistry': 83
        },
        'attendance': {
            'total_classes': 45,
            'attended': 44,
            'percentage': 97.8
        },
        'progress': {
            'completion': 82,
            'status': 'Excellent Progress',
            'performance': 'Very Good'
        }
    },
    'STU005': {
        'id': 'STU005',
        'name': 'Vikram Dubey',
        'password': 'vikram123',
        'email': 'vikram@example.com',
        'phone': '+91 9876543214',
        'class': 'Class 9',
        'enrollment_date': '2024-01-25',
        'marks': {
            'Mathematics': 95,
            'Science': 92,
            'Physics': 94,
            'Chemistry': 90
        },
        'attendance': {
            'total_classes': 38,
            'attended': 37,
            'percentage': 97.4
        },
        'progress': {
            'completion': 90,
            'status': 'Excellent Progress',
            'performance': 'Excellent'
        }
    }
}

def authenticate_student(student_id, password):
    """
    Authenticate student with ID and password
    Returns student data if valid, None otherwise
    """
    student = STUDENTS.get(student_id)
    
    if student and student['password'] == password:
        # Return student data without password
        student_data = student.copy()
        student_data.pop('password', None)
        return student_data
    
    return None

def get_student(student_id):
    """
    Get student data by student ID
    Returns student data without password
    """
    student = STUDENTS.get(student_id)
    
    if student:
        student_data = student.copy()
        student_data.pop('password', None)
        return student_data
    
    return None

def get_all_students():
    """Get all students (without passwords)"""
    all_students = []
    for student_id, student in STUDENTS.items():
        student_data = student.copy()
        student_data.pop('password', None)
        all_students.append(student_data)
    return all_students
