"""
Google Sheets API Service for Attendance Management
Handles all interactions with Google Sheets with fallback to in-memory storage
"""

import os
import json
import uuid
from datetime import datetime

try:
    from google.auth.transport.requests import Request
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False

class GoogleSheetsService:
    def __init__(self):
        self.sheets_id = os.getenv('GOOGLE_SHEETS_ID', '')
        self.service = None
        self.classes = ['Class 8', 'Class 9', 'Class 10']
        self.initialized = False
        self.use_fallback = True
        
        # In-memory fallback storage
        self.students_data = {}
        self.attendance_data = {}
        self._init_fallback_storage()
        
        if self.sheets_id and GOOGLE_LIBS_AVAILABLE:
            try:
                self._initialize_service()
                self.use_fallback = False
                print("✓ Google Sheets API initialized successfully")
                self.initialized = True
            except Exception as e:
                print(f"⚠️ Google Sheets auth failed: {e}")
                print("⚠️ Using local storage fallback (data won't sync to Google Sheets)")
                print("⚠️ To enable Google Sheets: Add GOOGLE_SERVICE_ACCOUNT secret with service account JSON")
                self.use_fallback = True
    
    def _init_fallback_storage(self):
        """Initialize in-memory storage"""
        for cls in self.classes:
            self.students_data[cls] = []
            self.attendance_data[f"{cls}"] = {}
    
    def _initialize_service(self):
        """Initialize Google Sheets API service"""
        service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT', '')
        
        if not service_account_json:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT not configured. Add service account JSON to secrets.")
        
        # Parse service account JSON
        try:
            service_account_info = json.loads(service_account_json)
        except json.JSONDecodeError:
            raise ValueError("Invalid GOOGLE_SERVICE_ACCOUNT JSON format")
        
        # Create credentials with proper scopes
        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        
        self.service = build('sheets', 'v4', credentials=credentials)
        self._auto_setup_sheets()
    
    def _auto_setup_sheets(self):
        """Automatically create sheets for each class if they don't exist"""
        if not self.service or not self.sheets_id:
            return
        
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.sheets_id
            ).execute()
            
            existing_sheets = {sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])}
            
            for class_name in self.classes:
                if class_name not in existing_sheets:
                    self._create_class_sheet(class_name)
                    print(f"✓ Created sheet: {class_name}")
        except Exception as e:
            print(f"⚠️ Could not auto-setup sheets: {e}")
    
    def _create_class_sheet(self, class_name):
        """Create a new sheet for a class with headers"""
        if not self.service:
            return
        
        try:
            request_body = {
                'requests': [
                    {
                        'addSheet': {
                            'properties': {'title': class_name}
                        }
                    }
                ]
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheets_id,
                body=request_body
            ).execute()
            
            headers = ['Roll No', 'Student Name', 'Date', 'Status', 'Notes']
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheets_id,
                range=f"'{class_name}'!A1:E1",
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            
        except Exception as e:
            print(f"⚠️ Error creating sheet: {e}")
    
    def add_student(self, class_name, roll_no, name):
        """Add a student"""
        try:
            if self.use_fallback or not self.service:
                return self._add_student_local(class_name, roll_no, name)
            else:
                return self._add_student_sheets(class_name, roll_no, name)
        except Exception as e:
            print(f"❌ Add student error: {e}")
            return self._add_student_local(class_name, roll_no, name)
    
    def _add_student_local(self, class_name, roll_no, name):
        """Add student to local storage"""
        if class_name not in self.students_data:
            self.students_data[class_name] = []
        
        student = {
            'id': str(uuid.uuid4()),
            'roll_no': str(roll_no),
            'name': name,
            'class': class_name
        }
        self.students_data[class_name].append(student)
        print(f"✓ Added student {name} to {class_name} (local storage)")
        return True
    
    def _add_student_sheets(self, class_name, roll_no, name):
        """Add student to Google Sheets"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range=f"'{class_name}'!A:A"
            ).execute()
            
            rows = result.get('values', [])
            next_row = len(rows) + 1
            
            values = [[str(roll_no), name, '', '', '']]
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheets_id,
                range=f"'{class_name}'!A{next_row}:E{next_row}",
                valueInputOption='RAW',
                body={'values': values}
            ).execute()
            
            print(f"✓ Added student {name} to {class_name} (Google Sheets)")
            return True
        except Exception as e:
            print(f"❌ Google Sheets error: {e}")
            return self._add_student_local(class_name, roll_no, name)
    
    def get_students(self, class_name):
        """Get all students from a class"""
        try:
            if self.use_fallback or not self.service:
                return self.students_data.get(class_name, [])
            else:
                return self._get_students_sheets(class_name)
        except Exception as e:
            print(f"⚠️ Error getting students: {e}")
            return self.students_data.get(class_name, [])
    
    def _get_students_sheets(self, class_name):
        """Get students from Google Sheets"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range=f"'{class_name}'!A2:B"
            ).execute()
            
            rows = result.get('values', [])
            students = []
            
            for row in rows:
                if len(row) >= 2:
                    students.append({
                        'id': str(uuid.uuid4()),
                        'roll_no': row[0],
                        'name': row[1],
                        'class': class_name
                    })
            
            return students
        except Exception as e:
            print(f"⚠️ Google Sheets error: {e}")
            return self.students_data.get(class_name, [])
    
    def delete_student(self, class_name, roll_no):
        """Delete a student"""
        try:
            if self.use_fallback or not self.service:
                return self._delete_student_local(class_name, roll_no)
            else:
                return self._delete_student_sheets(class_name, roll_no)
        except Exception as e:
            print(f"❌ Delete error: {e}")
            return self._delete_student_local(class_name, roll_no)
    
    def _delete_student_local(self, class_name, roll_no):
        """Delete from local storage"""
        if class_name in self.students_data:
            self.students_data[class_name] = [
                s for s in self.students_data[class_name] 
                if s['roll_no'] != str(roll_no)
            ]
            return True
        return False
    
    def _delete_student_sheets(self, class_name, roll_no):
        """Delete from Google Sheets"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range=f"'{class_name}'!A:B"
            ).execute()
            
            rows = result.get('values', [])
            
            for i, row in enumerate(rows):
                if len(row) > 0 and row[0] == str(roll_no):
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.sheets_id,
                        range=f"'{class_name}'!A{i+1}:E{i+1}",
                        valueInputOption='RAW',
                        body={'values': [['', '', '', '', '']]}
                    ).execute()
                    return True
            
            return False
        except Exception as e:
            print(f"⚠️ Google Sheets error: {e}")
            return self._delete_student_local(class_name, roll_no)
    
    def submit_attendance(self, class_name, date, records):
        """Submit attendance"""
        try:
            if self.use_fallback or not self.service:
                return self._submit_attendance_local(class_name, date, records)
            else:
                return self._submit_attendance_sheets(class_name, date, records)
        except Exception as e:
            print(f"❌ Attendance error: {e}")
            return self._submit_attendance_local(class_name, date, records)
    
    def _submit_attendance_local(self, class_name, date, records):
        """Submit to local storage"""
        key = f"{class_name}_{date}"
        self.attendance_data[key] = records
        print(f"✓ Attendance submitted to {class_name} for {date} (local storage)")
        return True
    
    def _submit_attendance_sheets(self, class_name, date, records):
        """Submit to Google Sheets"""
        try:
            # Get all students
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range=f"'{class_name}'!A2:B"
            ).execute()
            
            rows = result.get('values', [])
            
            # Update attendance for each student
            for i, row in enumerate(rows, start=2):
                if len(row) > 0:
                    # Find matching record
                    for record in records:
                        self.service.spreadsheets().values().update(
                            spreadsheetId=self.sheets_id,
                            range=f"'{class_name}'!C{i}:E{i}",
                            valueInputOption='RAW',
                            body={'values': [[date, record.get('status', ''), record.get('notes', '')]]}
                        ).execute()
            
            print(f"✓ Attendance submitted to {class_name} for {date} (Google Sheets)")
            return True
        except Exception as e:
            print(f"⚠️ Google Sheets error: {e}")
            return self._submit_attendance_local(class_name, date, records)
    
    def get_attendance(self, class_name, date=None):
        """Get attendance records"""
        try:
            if self.use_fallback or not self.service:
                return self._get_attendance_local(class_name, date)
            else:
                return self._get_attendance_sheets(class_name, date)
        except Exception as e:
            print(f"⚠️ Error getting attendance: {e}")
            return self._get_attendance_local(class_name, date)
    
    def _get_attendance_local(self, class_name, date=None):
        """Get from local storage"""
        records = []
        
        # Get students from this class
        students = self.students_data.get(class_name, [])
        
        # Check attendance data
        for key, attendance_list in self.attendance_data.items():
            if key.startswith(class_name):
                for attendance in attendance_list:
                    if isinstance(attendance, dict):
                        records.append(attendance)
        
        return records if records else []
    
    def _get_attendance_sheets(self, class_name, date=None):
        """Get from Google Sheets"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range=f"'{class_name}'!A2:E"
            ).execute()
            
            rows = result.get('values', [])
            records = []
            
            for row in rows:
                if len(row) >= 5:
                    if date and len(row) > 2 and row[2] != date:
                        continue
                    
                    records.append({
                        'roll_no': row[0] if len(row) > 0 else '',
                        'student_name': row[1] if len(row) > 1 else '',
                        'date': row[2] if len(row) > 2 else '',
                        'status': row[3] if len(row) > 3 else '',
                        'notes': row[4] if len(row) > 4 else ''
                    })
            
            return records
        except Exception as e:
            print(f"⚠️ Google Sheets error: {e}")
            return self._get_attendance_local(class_name, date)
    
    def is_initialized(self):
        """Check if service is initialized (will use fallback if Google Sheets fails)"""
        return True  # Always return True - we have fallback

# Initialize service globally
gs_service = GoogleSheetsService()
