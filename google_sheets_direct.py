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
            target_id = str(student_id).strip().lower()
            for i, cell_value in enumerate(cells):
                if str(cell_value).strip().lower() == target_id:
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
                if row and any(row):  # Check if row is not completely empty
                    student = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            val = row[i]
                            if header.endswith('_json'):
                                try:
                                    student[header.replace('_json', '')] = json.loads(val) if val else []
                                except:
                                    student[header.replace('_json', '')] = []
                            else:
                                student[header] = val
                        else:
                            # Handle missing columns in row
                            if header.endswith('_json'):
                                student[header.replace('_json', '')] = []
                            else:
                                student[header] = ''
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
                print(f"[DEBUG] Student ID {student_id} not found via _find_row_by_id")
                return None
            
            # Read all rows once to get headers and the specific student row
            all_values = self.sheet.get_all_values()
            if not all_values or len(all_values) < row_num:
                print(f"[DEBUG] Sheet empty or row_num {row_num} out of range")
                return None
                
            headers = [h.strip().lower() for h in all_values[0]]
            row = all_values[row_num - 1] # Row numbers start at 1
            
            student = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    val = str(row[i]).strip()
                    if header.endswith('_json'):
                        try:
                            student[header.replace('_json', '')] = json.loads(val) if val else []
                        except:
                            student[header.replace('_json', '')] = []
                    else:
                        student[header] = val
                else:
                    if header.endswith('_json'):
                        student[header.replace('_json', '')] = []
                    else:
                        student[header] = ''
            
            # Add original headers as keys too for compatibility
            original_headers = [h.strip() for h in all_values[0]]
            for i, h in enumerate(original_headers):
                if i < len(row):
                    # Only add if not already added to avoid case conflicts
                    if h not in student:
                        student[h] = str(row[i]).strip()
            
            print(f"[INFO] Retrieved student {student_id}: { {k:v for k,v in student.items() if 'password' not in k.lower()} }")
            return student
        except Exception as e:
            print(f"[ERROR] Failed to get student {student_id}: {e}")
            return None
    
    def authenticate_student(self, student_id, password):
        """Authenticate student by ID and password"""
        try:
            student_id = str(student_id).strip()
            password = str(password).strip()
            print(f"[DEBUG] Raw Login Attempt - ID: '{student_id}', PWD: '{password}'")
            
            # Aggressive sheet re-sync
            self.sheet = self.spreadsheet.worksheet("Students")
            student = self.get_student(student_id)
            
            if not student:
                print(f"[WARNING] Student '{student_id}' not found in sheet after re-sync")
                return None
            
            # Aggressive cleaning for comparison
            stored_id = str(student.get('id', '')).strip().lower()
            provided_id = student_id.lower()
            
            # Map all variations of password header
            stored_password = ""
            for key, val in student.items():
                if key.lower().strip() == 'password':
                    stored_password = str(val).strip()
                    break
            
            print(f"[DEBUG] Auth Compare - StoredID: '{stored_id}', ProvID: '{provided_id}', Match: {stored_id == provided_id}")
            print(f"[DEBUG] Auth Compare - StoredPWD: '{stored_password}', ProvPWD: '{password}', Match: {stored_password == password}")
            
            if stored_id == provided_id and stored_password == password:
                result = {k: v for k, v in student.items() if k.lower().strip() != 'password'}
                print(f"[INFO] Student {student_id} authenticated successfully")
                return result
            
            print(f"[WARNING] Auth failure for {student_id}")
            return None
        except Exception as e:
            print(f"[ERROR] Failed to authenticate student: {e}")
            return None
    
    def add_student(self, data):
        """Add a new student record"""
        try:
            headers = self._get_headers()
            row = []
            
            # CRITICAL: Clean password during addition
            if 'password' in data:
                data['password'] = str(data['password']).strip()
            
            for header in headers:
                if header.endswith('_json'):
                    key = header.replace('_json', '')
                    value = data.get(key, [])
                    row.append(json.dumps(value) if isinstance(value, list) else value)
                else:
                    row.append(str(data.get(header, '')).strip())
            
            self.sheet.append_row(row)
            print(f"[INFO] Added student {data.get('id')} with cleaned password")
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
            
            # CRITICAL: Clean password during update
            if 'password' in data:
                data['password'] = str(data['password']).strip()
            
            headers = self._get_headers()
            row = []
            
            for header in headers:
                if header.endswith('_json'):
                    key = header.replace('_json', '')
                    value = data.get(key, [])
                    row.append(json.dumps(value) if isinstance(value, list) else value)
                else:
                    row.append(str(data.get(header, '')).strip())
            
            # Update the row
            self.sheet.delete_rows(row_num)
            self.sheet.insert_row(row, row_num)
            
            print(f"[INFO] Updated student {student_id} with cleaned password")
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
