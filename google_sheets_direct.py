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
            
            # Clean common pasting errors
            service_account_json = service_account_json.strip()
            if service_account_json.startswith("'") and service_account_json.endswith("'"):
                service_account_json = service_account_json[1:-1]
            if service_account_json.startswith('"') and service_account_json.endswith('"'):
                service_account_json = service_account_json[1:-1]
                
            # Authenticate with Google Sheets API
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Use raw string handling to preserve the private key format exactly as pasted
            raw_key = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY', '').strip()
            
            # Remove wrapping quotes if present
            if (raw_key.startswith("'") and raw_key.endswith("'")) or (raw_key.startswith('"') and raw_key.endswith('"')):
                raw_key = raw_key[1:-1]

            try:
                # First attempt: direct parse
                service_account_info = json.loads(raw_key)
            except Exception:
                try:
                    # Second attempt: handle escaped newlines
                    fixed_key = raw_key.replace('\\n', '\n')
                    service_account_info = json.loads(fixed_key)
                except Exception:
                    # Third attempt: handle literal newlines and control characters
                    # (This is often where 'Invalid control character' errors come from)
                    import re
                    # Remove non-printable characters except for whitespace
                    cleaned_key = "".join(c for c in raw_key if c.isprintable() or c in "\n\r\t")
                    service_account_info = json.loads(cleaned_key)

            # Re-fetch Sheet ID and set it properly to fix LSP error
            self.sheet_id = os.environ.get('GOOGLE_SHEETS_ID')
            if not self.sheet_id:
                raise ValueError("GOOGLE_SHEETS_ID environment variable not set")
            
            credentials = Credentials.from_service_account_info(
                service_account_info,
                scopes=scopes
            )
            
            self.client = gspread.authorize(credentials)
            self.spreadsheet = self.client.open_by_key(self.sheet_id)
            
            # Ensure required sheets exist
            self.sheet = self._get_or_create_sheet("Students", ["id", "name", "password", "email", "phone", "student_class", "enrollment_date"])
            self.auth_sheet = self._get_or_create_sheet("StudentAuth", ["Username", "Password", "StudentID"])
            self.tests_sheet = self._get_or_create_sheet("Tests", ["StudentID", "TestName", "Date", "Marks", "Total"])
            self.attendance_sheet = self._get_or_create_sheet("Attendance", ["StudentID", "Date", "Status"])
            
            print("[INFO] Google Sheets service initialized successfully")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize Google Sheets service: {e}")
            raise

    def _get_or_create_sheet(self, title, headers):
        try:
            worksheet = self.spreadsheet.worksheet(title)
            # Check if headers exist
            rows = worksheet.get_all_values()
            if not rows:
                worksheet.append_row(headers)
            return worksheet
        except gspread.exceptions.WorksheetNotFound:
            worksheet = self.spreadsheet.add_worksheet(title=title, rows=1000, cols=len(headers) + 5)
            worksheet.append_row(headers)
            return worksheet
        except Exception as e:
            # Handle potential race conditions by trying to fetch again
            try:
                return self.spreadsheet.worksheet(title)
            except:
                raise e
    
    def _get_headers(self):
        try:
            return self.sheet.row_values(1)
        except:
            return []
    
    def _find_row_by_id(self, student_id):
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
        try:
            headers = self._get_headers()
            rows = self.sheet.get_all_values()
            students = []
            for row in rows[1:]:
                if row and any(row):
                    student = {headers[i]: row[i] for i in range(len(headers)) if i < len(row)}
                    students.append(student)
            return students
        except:
            return []
    
    def get_student(self, student_id):
        """Get full student data including tests and attendance from separate sheets"""
        try:
            all_values = self.sheet.get_all_values()
            if not all_values: return None
            headers = [str(h).strip().lower() for h in all_values[0]]
            id_col_idx = headers.index('id') if 'id' in headers else -1
            if id_col_idx == -1: return None
            
            target_id = str(student_id).strip().lower()
            student = None
            for row in all_values[1:]:
                if len(row) > id_col_idx and str(row[id_col_idx]).strip().lower() == target_id:
                    student = {headers[i]: row[i] for i in range(len(headers)) if i < len(row)}
                    break
            
            if student:
                # Fetch Tests
                all_tests = self.tests_sheet.get_all_values()
                student['tests'] = []
                if all_tests and len(all_tests) > 1:
                    test_headers = [h.lower() for h in all_tests[0]]
                    s_id_idx = test_headers.index('studentid')
                    for t_row in all_tests[1:]:
                        if len(t_row) > s_id_idx and str(t_row[s_id_idx]).strip().lower() == target_id:
                            student['tests'].append({test_headers[i]: t_row[i] for i in range(len(test_headers)) if i < len(t_row)})
                
                # Fetch Attendance
                all_att = self.attendance_sheet.get_all_values()
                student['attendance_log'] = []
                if all_att and len(all_att) > 1:
                    att_headers = [h.lower() for h in all_att[0]]
                    s_id_idx = att_headers.index('studentid')
                    for a_row in all_att[1:]:
                        if len(a_row) > s_id_idx and str(a_row[s_id_idx]).strip().lower() == target_id:
                            student['attendance_log'].append({att_headers[i]: a_row[i] for i in range(len(att_headers)) if i < len(a_row)})
                
                # Calculate attendance percentage
                if student['attendance_log']:
                    present = len([a for a in student['attendance_log'] if a.get('status', '').lower() == 'present'])
                    total = len(student['attendance_log'])
                    student['attendance_percentage'] = (present/total)*100 if total > 0 else 0
                    student['progress'] = {"completion": student['attendance_percentage'], "status": "In Progress"}
                else:
                    student['attendance_percentage'] = 0
                    student['progress'] = {"completion": 0, "status": "New"}

            return student
        except Exception as e:
            print(f"Error in get_student: {e}")
            return None

    def sync_auth_record(self, username, password, student_id):
        try:
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
        try:
            # First attempt: Exact match from StudentAuth sheet
            all_auth = self.auth_sheet.get_all_values()
            if not all_auth or len(all_auth) < 2: return None
            
            def super_clean(s):
                return "".join(str(s).split()).lower()
            
            p_user = super_clean(username)
            p_pass = super_clean(password)
            
            for row in all_auth[1:]:
                if len(row) < 2: continue
                # Match username and password
                if super_clean(row[0]) == p_user and super_clean(row[1]) == p_pass:
                    student_id = row[2] if len(row) > 2 else row[0]
                    return self.get_student(student_id)
            
            # Fallback: Check Students sheet directly if Auth sheet fails
            students = self.get_all_students()
            for s in students:
                if super_clean(s.get('name', '')) == p_user and super_clean(s.get('password', '')) == p_pass:
                    return self.get_student(s.get('id'))
                    
            return None
        except Exception as e:
            print(f"Error in authenticate_student: {e}")
            return None
    
    def add_student(self, data):
        try:
            headers = self._get_headers()
            row = [str(data.get(h, '')).strip() for h in headers]
            self.sheet.append_row(row)
            return True
        except:
            return False

    def update_student(self, student_id, data):
        try:
            row_num = self._find_row_by_id(student_id)
            if not row_num: return False
            headers = self._get_headers()
            row = [str(data.get(h, '')).strip() for h in headers]
            self.sheet.delete_rows(row_num)
            self.sheet.insert_row(row, row_num)
            
            # Sync tests
            if 'tests' in data:
                all_tests = self.tests_sheet.get_all_values()
                if all_tests:
                    rows_to_delete = []
                    for i, t_row in enumerate(all_tests[1:], 2):
                        if len(t_row) > 0 and str(t_row[0]).strip().lower() == str(student_id).strip().lower():
                            rows_to_delete.append(i)
                    for r in reversed(rows_to_delete):
                        self.tests_sheet.delete_rows(r)
                for t in data['tests']:
                    self.tests_sheet.append_row([str(student_id), t.get('name'), t.get('date'), str(t.get('marks')), str(t.get('total'))])

            # Sync attendance
            if 'attendance_log' in data:
                all_att = self.attendance_sheet.get_all_values()
                if all_att:
                    rows_to_delete = []
                    for i, a_row in enumerate(all_att[1:], 2):
                        if len(a_row) > 0 and str(a_row[0]).strip().lower() == str(student_id).strip().lower():
                            rows_to_delete.append(i)
                    for r in reversed(rows_to_delete):
                        self.attendance_sheet.delete_rows(r)
                for a in data['attendance_log']:
                    self.attendance_sheet.append_row([str(student_id), a.get('date'), a.get('status')])
            
            return True
        except Exception as e:
            print(f"Error in update_student: {e}")
            return False
    
    def delete_student(self, student_id):
        try:
            row_num = self._find_row_by_id(student_id)
            if not row_num: return False
            self.sheet.delete_rows(row_num)
            return True
        except:
            return False

sheets_service = None
def init_sheets_service(app):
    global sheets_service
    try:
        sheets_service = GoogleSheetsService()
    except Exception as e:
        print(f"[ERROR] Failed to initialize sheets service: {e}")

def get_sheets_service():
    return sheets_service
