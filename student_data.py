"""
Backward compatibility wrapper for student data operations
Now uses Google Sheets via sheets_service
"""
from sheets_service import get_sheets_service
from datetime import datetime

# Legacy compatibility functions that now use Google Sheets

def init_db(app):
    """Legacy function - no longer needed with Google Sheets"""
    print("Database initialization skipped - using Google Sheets")
    pass

def authenticate_student(student_id, password):
    """Authenticate a student via Google Sheets"""
    service = get_sheets_service()
    if not service:
        return None
    return service.authenticate_student(student_id, password)

def get_student(student_id):
    """Get a single student from Google Sheets"""
    service = get_sheets_service()
    if not service:
        return None
    return service.get_student(student_id)

def get_all_students():
    """Get all students from Google Sheets"""
    service = get_sheets_service()
    if not service:
        return []
    students = service.get_all_students()
    return students if isinstance(students, list) else []

def add_student(data):
    """Add a new student to Google Sheets"""
    service = get_sheets_service()
    if not service:
        return False
    return service.add_student(data)

def update_student(student_id, data):
    """Update student data in Google Sheets"""
    service = get_sheets_service()
    if not service:
        return False
    data['id'] = student_id
    return service.update_student(student_id, data)

def delete_student(student_id):
    """Delete a student from Google Sheets"""
    service = get_sheets_service()
    if not service:
        return False
    return service.delete_student(student_id)
