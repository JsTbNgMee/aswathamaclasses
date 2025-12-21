"""
Google Apps Script Service for Attendance Management
Uses Google Apps Script deployment instead of direct API authentication
"""

import os
import requests
import json
from datetime import datetime

class GoogleAppsScriptService:
    def __init__(self):
        self.script_url = os.getenv('GOOGLE_APPS_SCRIPT_URL', '')
        self.initialized = bool(self.script_url)
        
        # Fallback in-memory storage
        self.students_data = {}
        self.attendance_data = {}
        self._init_fallback()
        
        if self.initialized:
            print("✓ Google Apps Script service configured")
            try:
                self._initialize_script()
            except Exception as e:
                print(f"⚠️ Could not initialize Google Apps Script: {e}")
    
    def _init_fallback(self):
        """Initialize fallback storage"""
        for cls in ['Class 8', 'Class 9', 'Class 10']:
            self.students_data[cls] = []
            self.attendance_data[cls] = {}
    
    def _initialize_script(self):
        """Initialize the Google Apps Script"""
        try:
            response = requests.post(
                self.script_url,
                json={'action': 'init'},
                timeout=10
            )
            if response.status_code == 200:
                print("✓ Google Apps Script initialized")
        except Exception as e:
            print(f"⚠️ Initialization call failed: {e}")
    
    def _call_script(self, action, data):
        """Call Google Apps Script with action and data"""
        if not self.initialized:
            return None
        
        try:
            payload = {'action': action, **data}
            response = requests.post(
                self.script_url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Google Apps Script error ({action}): {e}")
            return None
    
    def add_student(self, class_name, roll_no, name):
        """Add a student"""
        # Try Google Apps Script first
        if self.initialized:
            result = self._call_script('add_student', {
                'className': class_name,
                'rollNo': str(roll_no),
                'name': name
            })
            if result and result.get('success'):
                print(f"✓ Student added to Google Apps Script")
                return True
        
        # Fallback to local storage
        return self._add_student_local(class_name, roll_no, name)
    
    def _add_student_local(self, class_name, roll_no, name):
        """Add to local storage"""
        if class_name not in self.students_data:
            self.students_data[class_name] = []
        
        self.students_data[class_name].append({
            'roll_no': str(roll_no),
            'name': name,
            'class': class_name
        })
        print(f"✓ Student added to local storage")
        return True
    
    def get_students(self, class_name):
        """Get all students"""
        # Try Google Apps Script first
        if self.initialized:
            result = self._call_script('get_students', {'className': class_name})
            if result and result.get('success'):
                return result.get('students', [])
        
        # Fallback to local
        return self.students_data.get(class_name, [])
    
    def delete_student(self, class_name, roll_no):
        """Delete a student"""
        # Try Google Apps Script first
        if self.initialized:
            result = self._call_script('delete_student', {
                'className': class_name,
                'rollNo': str(roll_no)
            })
            if result and result.get('success'):
                return True
        
        # Fallback to local
        if class_name in self.students_data:
            self.students_data[class_name] = [
                s for s in self.students_data[class_name]
                if s['roll_no'] != str(roll_no)
            ]
            return True
        return False
    
    def submit_attendance(self, class_name, date, records):
        """Submit attendance"""
        # Try Google Apps Script first
        if self.initialized:
            result = self._call_script('submit_attendance', {
                'className': class_name,
                'date': date,
                'records': records
            })
            if result and result.get('success'):
                print(f"✓ Attendance submitted to Google Apps Script")
                return True
        
        # Fallback to local
        self.attendance_data[f"{class_name}_{date}"] = records
        print(f"✓ Attendance submitted to local storage")
        return True
    
    def get_attendance(self, class_name, date=None):
        """Get attendance records"""
        # Try Google Apps Script first
        if self.initialized:
            result = self._call_script('get_attendance', {
                'className': class_name,
                'date': date or ''
            })
            if result and result.get('success'):
                return result.get('records', [])
        
        # Fallback to local
        records = []
        for key, data in self.attendance_data.items():
            if key.startswith(class_name):
                if isinstance(data, list):
                    records.extend(data)
        return records
    
    def is_initialized(self):
        """Always return True - we have fallback"""
        return True

# Initialize service globally
gs_service = GoogleAppsScriptService()
