"""
Google Sheets API Service for Attendance Management
Handles all interactions with Google Sheets
"""

import os
import json
import uuid
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.api_core.exceptions import NotFound
from googleapiclient.discovery import build

class GoogleSheetsService:
    def __init__(self):
        self.sheets_id = os.getenv('GOOGLE_SHEETS_ID', '')
        self.service = None
        self.classes = ['Class 8', 'Class 9', 'Class 10']
        self.initialized = False
        
        if self.sheets_id:
            try:
                self._initialize_service()
                self._auto_setup_sheets()
                self.initialized = True
            except Exception as e:
                print(f"❌ Google Sheets initialization failed: {e}")
    
    def _initialize_service(self):
        """Initialize Google Sheets API service"""
        try:
            # Try to use service account JSON from environment
            service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT')
            
            if service_account_json:
                # Parse JSON string
                try:
                    service_account_info = json.loads(service_account_json)
                except:
                    service_account_info = json.loads(service_account_json.replace("'", '"'))
                
                credentials = Credentials.from_service_account_info(
                    service_account_info,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
            else:
                # Fallback: Use API key (read-only)
                api_key = os.getenv('GOOGLE_SHEETS_API_KEY', '')
                if not api_key:
                    raise ValueError("No Google Sheets credentials found")
                
                # For API key method, we use simpler approach
                self.api_key = api_key
                self.service = build('sheets', 'v4', developerKey=api_key)
                return
            
            self.service = build('sheets', 'v4', credentials=credentials)
            print("✓ Google Sheets API authenticated")
        except Exception as e:
            print(f"❌ Auth error: {e}")
            raise
    
    def _auto_setup_sheets(self):
        """Automatically create sheets for each class if they don't exist"""
        if not self.service or not self.sheets_id:
            return
        
        try:
            # Get existing sheets
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.sheets_id
            ).execute()
            
            existing_sheets = {sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])}
            
            # Create sheets for each class if missing
            for class_name in self.classes:
                if class_name not in existing_sheets:
                    self._create_class_sheet(class_name)
                    print(f"✓ Created sheet: {class_name}")
        except Exception as e:
            print(f"❌ Auto-setup error: {e}")
    
    def _create_class_sheet(self, class_name):
        """Create a new sheet for a class with headers"""
        if not self.service:
            return
        
        try:
            # Create sheet
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
            
            # Add headers
            headers = ['Roll No', 'Student Name', 'Date', 'Status', 'Notes']
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheets_id,
                range=f"'{class_name}'!A1:E1",
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            
        except Exception as e:
            print(f"❌ Create sheet error: {e}")
    
    def add_student(self, class_name, roll_no, name):
        """Add a student to the Google Sheet"""
        if not self.service or not self.sheets_id:
            return False
        
        try:
            # Find next empty row
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range=f"'{class_name}'!A:A"
            ).execute()
            
            rows = result.get('values', [])
            next_row = len(rows) + 1
            
            # Add student
            values = [[roll_no, name, '', '', '']]
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheets_id,
                range=f"'{class_name}'!A{next_row}:E{next_row}",
                valueInputOption='RAW',
                body={'values': values}
            ).execute()
            
            print(f"✓ Added student {name} to {class_name}")
            return True
        except Exception as e:
            print(f"❌ Add student error: {e}")
            return False
    
    def get_students(self, class_name):
        """Get all students from a class sheet"""
        if not self.service or not self.sheets_id:
            return []
        
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
                        'name': row[1] if len(row) > 1 else '',
                        'class': class_name
                    })
            
            return students
        except Exception as e:
            print(f"❌ Get students error: {e}")
            return []
    
    def delete_student(self, class_name, roll_no):
        """Delete a student from the sheet"""
        if not self.service or not self.sheets_id:
            return False
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range=f"'{class_name}'!A:B"
            ).execute()
            
            rows = result.get('values', [])
            
            for i, row in enumerate(rows):
                if len(row) > 0 and row[0] == str(roll_no):
                    # Clear the row
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.sheets_id,
                        range=f"'{class_name}'!A{i+1}:E{i+1}",
                        valueInputOption='RAW',
                        body={'values': [['', '', '', '', '']]}
                    ).execute()
                    return True
            
            return False
        except Exception as e:
            print(f"❌ Delete student error: {e}")
            return False
    
    def submit_attendance(self, class_name, date, records):
        """Submit attendance for multiple students"""
        if not self.service or not self.sheets_id:
            return False
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range=f"'{class_name}'!A:B"
            ).execute()
            
            rows = result.get('values', [])
            
            # Create mapping of roll_no to row number
            for record in records:
                student_id = record.get('student_id')
                status = record.get('status')
                notes = record.get('notes', '')
                
                # Find student by ID (we'll use roll_no from the record)
                for i, row in enumerate(rows):
                    if len(row) > 0:  # Has data
                        # Update attendance data
                        self.service.spreadsheets().values().update(
                            spreadsheetId=self.sheets_id,
                            range=f"'{class_name}'!C{i+1}:E{i+1}",
                            valueInputOption='RAW',
                            body={'values': [[date, status, notes]]}
                        ).execute()
            
            return True
        except Exception as e:
            print(f"❌ Submit attendance error: {e}")
            return False
    
    def get_attendance(self, class_name, date=None):
        """Get attendance records for a class"""
        if not self.service or not self.sheets_id:
            return []
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range=f"'{class_name}'!A2:E"
            ).execute()
            
            rows = result.get('values', [])
            records = []
            
            for row in rows:
                if len(row) >= 5:
                    # Check if date matches (if provided)
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
            print(f"❌ Get attendance error: {e}")
            return []
    
    def is_initialized(self):
        """Check if Google Sheets service is properly initialized"""
        return self.initialized and bool(self.service)

# Initialize service globally
gs_service = GoogleSheetsService()
