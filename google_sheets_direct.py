"""
Google Sheets Direct Integration - Uses official Google Sheets API via gspread
Authenticates with service account credentials and reads/writes directly to Google Sheets
"""
import os
import json
import gspread
from google.oauth2.service_account import Credentials

class GoogleSheetsService:
    def __init__(self):
        """Initialize Google Sheets service with service account credentials"""
        try:
            # Get service account key from environment
            service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
            if not service_account_json:
                raise ValueError("GOOGLE_SERVICE_ACCOUNT_KEY environment variable not set")
            
            # Parse the JSON key
            service_account_info = json.loads(service_account_json)
            
            # Get Sheet ID from environment
            self.sheet_id = os.environ.get('GOOGLE_SHEETS_ID')
            if not self.sheet_id:
                raise ValueError("GOOGLE_SHEETS_ID environment variable not set")
            
            # Authenticate with Google Sheets API
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            credentials = Credentials.from_service_account_info(
                service_account_info,
                scopes=scopes
            )
            
            self.client = gspread.authorize(credentials)
            self.spreadsheet = self.client.open_by_key(self.sheet_id)
            
            # Get or create the Students sheet
            try:
                self.sheet = self.spreadsheet.worksheet("Students")
                print("[INFO] Using existing 'Students' sheet")
            except gspread.exceptions.WorksheetNotFound:
                try:
                    self.sheet = self.spreadsheet.add_worksheet("Students", rows=1000, cols=10)
                    print("[INFO] Created new 'Students' sheet")
                except Exception as e:
                    print(f"[WARNING] Could not create sheet, using first sheet: {e}")
                    self.sheet = self.spreadsheet.sheet1
            
            # Initialize sheet with headers if empty
            self._initialize_headers()
            print("[INFO] Google Sheets service initialized successfully")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize Google Sheets service: {e}")
            raise
    
    def _initialize_headers(self):
        """Create header row if sheet is empty"""
        try:
            if self.sheet.cell(1, 1).value is None:
                headers = [
                    'id', 'name', 'password', 'email', 'phone', 'student_class',
                    'enrollment_date', 'tests_json', 'attendance_log_json', 'progress_json'
                ]
                self.sheet.insert_row(headers, 1)
                print("[INFO] Sheet headers initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize headers: {e}")
    
    def _get_headers(self):
        """Get header row"""
        try:
            return self.sheet.row_values(1)
        except Exception as e:
            print(f"[ERROR] Failed to get headers: {e}")
            return []
    
    def _find_row_by_id(self, student_id):
        """Find row index by student ID"""
        try:
            id_index = self._get_headers().index('id')
            cells = self.sheet.col_values(id_index + 1)
            for i, cell_value in enumerate(cells):
                if cell_value == student_id:
                    return i + 1  # Row numbers start at 1
            return None
        except Exception as e:
            print(f"[ERROR] Failed to find row by ID: {e}")
            return None
    
    def get_all_students(self):
        """Get all student records"""
        try:
            headers = self._get_headers()
            rows = self.sheet.get_all_values()
            
            students = []
            for row in rows[1:]:  # Skip header row
                if row and row[0]:  # Check if ID exists
                    student = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            if header.endswith('_json'):
                                try:
                                    student[header.replace('_json', '')] = json.loads(row[i]) if row[i] else []
                                except:
                                    student[header.replace('_json', '')] = []
                            else:
                                student[header] = row[i]
                    students.append(student)
            
            print(f"[INFO] Retrieved {len(students)} students from sheet")
            return students
        except Exception as e:
            print(f"[ERROR] Failed to get all students: {e}")
            return []
    
    def get_student(self, student_id):
        """Get a single student by ID"""
        try:
            row_num = self._find_row_by_id(student_id)
            if not row_num:
                return None
            
            headers = self._get_headers()
            row = self.sheet.row_values(row_num)
            
            student = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    if header.endswith('_json'):
                        try:
                            student[header.replace('_json', '')] = json.loads(row[i]) if row[i] else []
                        except:
                            student[header.replace('_json', '')] = []
                    else:
                        student[header] = row[i]
            
            print(f"[INFO] Retrieved student {student_id}")
            return student
        except Exception as e:
            print(f"[ERROR] Failed to get student {student_id}: {e}")
            return None
    
    def authenticate_student(self, student_id, password):
        """Authenticate student by ID and password"""
        try:
            print(f"[DEBUG] Attempting to authenticate student: {student_id}")
            student = self.get_student(student_id)
            if not student:
                print(f"[WARNING] Student {student_id} not found in sheet")
                return None
            
            # Strip whitespace and ensure string comparison
            stored_password = str(student.get('password', '')).strip()
            provided_password = str(password).strip()
            
            print(f"[DEBUG] Stored password: '{stored_password}', Provided password: '{provided_password}'")
            
            if stored_password == provided_password:
                # Return student data without password
                result = {k: v for k, v in student.items() if k != 'password'}
                print(f"[INFO] Student {student_id} authenticated successfully")
                return result
            else:
                print(f"[WARNING] Password mismatch for student {student_id}")
            return None
        except Exception as e:
            print(f"[ERROR] Failed to authenticate student: {e}")
            return None
    
    def add_student(self, data):
        """Add a new student record"""
        try:
            headers = self._get_headers()
            row = []
            
            for header in headers:
                if header.endswith('_json'):
                    key = header.replace('_json', '')
                    value = data.get(key, [])
                    row.append(json.dumps(value) if isinstance(value, list) else value)
                else:
                    row.append(data.get(header, ''))
            
            self.sheet.append_row(row)
            print(f"[INFO] Added student {data.get('id')}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to add student: {e}")
            return False
    
    def update_student(self, student_id, data):
        """Update student record"""
        try:
            row_num = self._find_row_by_id(student_id)
            if not row_num:
                print(f"[WARNING] Student {student_id} not found")
                return False
            
            headers = self._get_headers()
            row = []
            
            for header in headers:
                if header.endswith('_json'):
                    key = header.replace('_json', '')
                    value = data.get(key, [])
                    row.append(json.dumps(value) if isinstance(value, list) else value)
                else:
                    row.append(data.get(header, ''))
            
            # Update the row
            self.sheet.delete_rows(row_num)
            self.sheet.insert_row(row, row_num)
            
            print(f"[INFO] Updated student {student_id}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to update student {student_id}: {e}")
            return False
    
    def delete_student(self, student_id):
        """Delete a student record"""
        try:
            row_num = self._find_row_by_id(student_id)
            if not row_num:
                print(f"[WARNING] Student {student_id} not found")
                return False
            
            self.sheet.delete_rows(row_num)
            print(f"[INFO] Deleted student {student_id}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to delete student {student_id}: {e}")
            return False

# Global instance
sheets_service = None

def init_sheets_service(app):
    """Initialize sheets service"""
    global sheets_service
    try:
        sheets_service = GoogleSheetsService()
    except Exception as e:
        print(f"[ERROR] Failed to initialize sheets service: {e}")

def get_sheets_service():
    """Get the global sheets service instance"""
    return sheets_service
