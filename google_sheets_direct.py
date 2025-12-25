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
        """Get a single student by ID with aggressive logging"""
        try:
            print(f"[DEBUG] Fetching student ID: {student_id}")
            all_values = self.sheet.get_all_values()
            if not all_values:
                print("[ERROR] Sheet is completely empty")
                return None
            
            headers = [str(h).strip().lower() for h in all_values[0]]
            print(f"[DEBUG] Raw Headers: {all_values[0]}")
            print(f"[DEBUG] Normalized Headers: {headers}")
            
            id_col_idx = -1
            for i, h in enumerate(headers):
                if h == 'id':
                    id_col_idx = i
                    break
            
            if id_col_idx == -1:
                print("[ERROR] No 'id' column found")
                return None
            
            target_id = str(student_id).strip().lower()
            for row in all_values[1:]:
                if len(row) > id_col_idx:
                    row_id = str(row[id_col_idx]).strip().lower()
                    if row_id == target_id:
                        student = {}
                        for i, h in enumerate(headers):
                            val = str(row[i]).strip() if i < len(row) else ""
                            student[h] = val
                            if h.endswith('_json'):
                                key = h.replace('_json', '')
                                try:
                                    student[key] = json.loads(val) if val else []
                                except:
                                    student[key] = []
                        print(f"[DEBUG] Found student: { {k:v for k,v in student.items() if 'password' not in k.lower()} }")
                        return student
            
            print(f"[WARNING] Student {student_id} not found in {len(all_values)-1} rows")
            return None
        except Exception as e:
            print(f"[ERROR] get_student: {e}")
            return None

    def authenticate_student(self, student_id, password):
        """Authenticate student with name-based username"""
        try:
            # Normalize provided username (ID or Name): remove spaces, lowercase
            provided_username = str(student_id).strip().lower()
            provided_password = str(password).strip().lower()
            
            print(f"[DEBUG] AUTH ATTEMPT - Username: '{provided_username}'")
            
            # Refresh connection
            self.sheet = self.spreadsheet.worksheet("Students")
            all_values = self.sheet.get_all_values()
            
            if not all_values:
                return None
                
            headers = [str(h).strip().lower() for h in all_values[0]]
            
            # Find ID, Name, and Password column indices
            id_idx = -1
            name_idx = -1
            pwd_idx = -1
            
            for i, h in enumerate(headers):
                if h == 'id': id_idx = i
                elif h == 'name': name_idx = i
                elif 'password' in h: pwd_idx = i
            
            for row in all_values[1:]:
                # Check match against ID OR Name
                match_found = False
                
                # Check ID Match
                if id_idx != -1 and len(row) > id_idx:
                    if str(row[id_idx]).strip().lower().replace('0', 'o') == provided_username.replace('0', 'o'):
                        match_found = True
                
                # Check Name Match (if no ID match)
                if not match_found and name_idx != -1 and len(row) > name_idx:
                    if str(row[name_idx]).strip().lower() == provided_username:
                        match_found = True
                
                if match_found:
                    if pwd_idx != -1 and len(row) > pwd_idx:
                        stored_password = str(row[pwd_idx]).strip().lower()
                        if stored_password == provided_password:
                            student = {headers[i]: str(row[i]).strip() for i in range(len(headers)) if i < len(row)}
                            print(f"[AUTH_SUCCESS] {provided_username}")
                            return student
            
            print(f"[AUTH_FAILED] No match for {provided_username}")
            return None
        except Exception as e:
            print(f"[ERROR] authenticate_student: {e}")
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
