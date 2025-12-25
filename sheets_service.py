"""
Google Sheets Service - Handles all student data operations via Google Apps Script API
"""
import os
import json
import requests
from datetime import datetime

class SheetsService:
    def __init__(self, app_script_url=None):
        self.app_script_url = app_script_url or os.environ.get('GOOGLE_APPS_SCRIPT_URL')
        if not self.app_script_url:
            raise ValueError("GOOGLE_APPS_SCRIPT_URL environment variable not set")
    
    def _make_request(self, action, method='GET', data=None):
        """Make HTTP request to Google Apps Script"""
        try:
            if method == 'GET':
                response = requests.get(
                    f"{self.app_script_url}?action={action}",
                    timeout=10
                )
            else:
                response = requests.post(
                    f"{self.app_script_url}?action={action}",
                    json=data,
                    timeout=10
                )
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Sheets API Error: {e}")
            return {"error": str(e)}
    
    def authenticate_student(self, student_id, password):
        """Authenticate a student"""
        result = self._make_request(
            'authenticate',
            method='POST',
            data={'id': student_id, 'password': password}
        )
        return result if result else None
    
    def get_student(self, student_id):
        """Get a single student"""
        result = self._make_request('get', data={'id': student_id})
        return result
    
    def get_all_students(self):
        """Get all students"""
        result = self._make_request('get_all')
        return result if isinstance(result, list) else []
    
    def add_student(self, data):
        """Add a new student"""
        result = self._make_request(
            'add',
            method='POST',
            data=data
        )
        return result.get('success', False)
    
    def update_student(self, student_id, data):
        """Update student data"""
        data['id'] = student_id
        result = self._make_request(
            'update',
            method='POST',
            data=data
        )
        return result.get('success', False)
    
    def delete_student(self, student_id):
        """Delete a student"""
        result = self._make_request(
            'delete',
            method='POST',
            data={'id': student_id}
        )
        return result.get('success', False)

# Global instance
sheets_service = None

def init_sheets_service(app):
    """Initialize sheets service"""
    global sheets_service
    try:
        sheets_service = SheetsService()
        print("Google Sheets service initialized")
    except ValueError as e:
        print(f"Warning: {e}")

def get_sheets_service():
    """Get the global sheets service instance"""
    return sheets_service
