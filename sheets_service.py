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
            url = f"{self.app_script_url}?action={action}"
            print(f"[DEBUG] {method} request to: {url[:80]}...")
            
            if method == 'GET':
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json=data, timeout=10)
            
            print(f"[DEBUG] Response status: {response.status_code}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Sheets API Error: {e}")
            return {"error": str(e)}
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
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
        print("Google Sheets service initialized successfully")
        # Test connection and initialize sheet structure
        try:
            sheets_service._make_request('get_all')
            print("[INFO] Google Sheets connection verified and headers initialized")
        except Exception as e:
            print(f"[WARNING] Could not verify sheet connection: {e}")
    except ValueError as e:
        print(f"[ERROR] {e}")

def get_sheets_service():
    """Get the global sheets service instance"""
    return sheets_service
