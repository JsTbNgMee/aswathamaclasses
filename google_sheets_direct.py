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
            except gspread.exceptions.WorksheetNotFound:
                try:
                    self.sheet = self.spreadsheet.add_worksheet("Students", rows=1000, cols=10)
                except:
                    self.sheet = self.spreadsheet.worksheet("Students")

            # Ensure 'StudentAuth' sheet exists
            try:
                self.auth_sheet = self.spreadsheet.worksheet("StudentAuth")
            except gspread.exceptions.WorksheetNotFound:
                try:
                    self.auth_sheet = self.spreadsheet.add_worksheet(title="StudentAuth", rows=100, cols=3)
                    self.auth_sheet.append_row(["Username", "Password", "StudentID"])
                except:
                    self.auth_sheet = self.spreadsheet.worksheet("StudentAuth")
            
            # Initialize sheet with headers if empty
            self._initialize_headers()
            print("[INFO] Google Sheets service initialized successfully")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize Google Sheets service: {e}")
            raise
    
    def _initialize_headers(self):
        """Create header row if sheet is empty"""
        try:
            if not self.sheet.get_all_values():
                headers = [
                    'id', 'name', 'password', 'email', 'phone', 'student_class',
                    'enrollment_date', 'tests_json', 'attendance_log_json', 'progress_json'
                ]
                self.sheet.insert_row(headers, 1)
        except:
            pass
    
    def _get_headers(self):
        """Get header row"""
        try:
            return self.sheet.row_values(1)
        except:
            return []
    
    def _find_row_by_id(self, student_id):
        """Find row index by student ID"""
        try:
            headers = self._get_headers()
            if not headers: return None
            id_index = headers.index('id')
            cells = self.sheet.col_values(id_index + 1)
            target_id = str(student_id).strip().lower()
            for i, cell_value in enumerate(cells):
                if str(cell_value).strip().lower() == target_id:
                    return i + 1
            return None
        except:
            return None
    
    def get_all_students(self):
        """Get all student records"""
        try:
            headers = self._get_headers()
            rows = self.sheet.get_all_values()
            students = []
            for row in rows[1:]:
                if row and any(row):
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
                    students.append(student)
            return students
        except:
            return []
    
    def get_student(self, student_id):
        """Get a single student by ID"""
        try:
            all_values = self.sheet.get_all_values()
            if not all_values: return None
            headers = [str(h).strip().lower() for h in all_values[0]]
            id_col_idx = -1
            for i, h in enumerate(headers):
                if h == 'id':
                    id_col_idx = i
                    break
            if id_col_idx == -1: return None
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
                        return student
            return None
        except:
            return None

    def sync_auth_record(self, username, password, student_id):
        """Sync or create a record in the StudentAuth sheet"""
        try:
            self.auth_sheet = self.spreadsheet.worksheet("StudentAuth")
            all_auth = self.auth_sheet.get_all_values()
            clean_user = "".join(str(username).split()).lower()
            found_idx = -1
            for i, row in enumerate(all_auth):
                if i == 0: continue
                if len(row) > 0 and "".join(str(row[0]).split()).lower() == clean_user:
                    found_idx = i + 1
                    break
            if found_idx != -1:
                self.auth_sheet.update_cell(found_idx, 2, str(password))
                self.auth_sheet.update_cell(found_idx, 3, str(student_id))
            else:
                self.auth_sheet.append_row([str(username), str(password), str(student_id)])
            return True
        except:
            return False

    def authenticate_student(self, username, password):
        """Authentication using the dedicated StudentAuth sheet"""
        try:
            self.auth_sheet = self.spreadsheet.worksheet("StudentAuth")
            all_auth = self.auth_sheet.get_all_values()
            if not all_auth or len(all_auth) < 2: return None
            def super_clean(s):
                return "".join(str(s).split()).lower().replace('0', 'o')
            p_user = super_clean(username)
            p_pass = super_clean(password)
            student_id = None
            for row in all_auth[1:]:
                if len(row) < 2: continue
                s_user = super_clean(row[0])
                s_pass = super_clean(row[1])
                if s_user == p_user and s_pass == p_pass:
                    student_id = row[2] if len(row) > 2 else row[0]
                    break
            if student_id:
                return self.get_student(student_id)
            return None
        except:
            return None
    
    def add_student(self, data):
        """Add a new student record"""
        try:
            headers = self._get_headers()
            row = []
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
            return True
        except:
            return False

    def update_student(self, student_id, data):
        """Update student record"""
        try:
            row_num = self._find_row_by_id(student_id)
            if not row_num: return False
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
            self.sheet.delete_rows(row_num)
            self.sheet.insert_row(row, row_num)
            return True
        except:
            return False
    
    def delete_student(self, student_id):
        """Delete a student record"""
        try:
            row_num = self._find_row_by_id(student_id)
            if not row_num: return False
            self.sheet.delete_rows(row_num)
            return True
        except:
            return False

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
