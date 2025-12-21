"""
ASWATHAMA CLASSES - Professional Coaching Institute Website
Backend: Flask
Author: Senior Full-Stack Developer
Description: A premium, minimalist coaching institute website with black & white theme
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
import os
import json
import uuid

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'aswathama-classes-secret-key'

# Admin credentials (change this to your desired password)
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

# Google Sheets API Configuration (User will add their credentials here)
GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID', '')
GOOGLE_SHEETS_API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY', '')

# In-memory storage (replace with database or Google Sheets later)
STUDENTS_DATA = {}  # {class: [{'id': '...', 'roll_no': '...', 'name': '...'}]}
ATTENDANCE_DATA = {}  # {date: [{student_id, status, notes}]}

# Initialize with sample data
def init_sample_data():
    """Initialize with sample data for testing"""
    for cls in ['Class 8', 'Class 9', 'Class 10']:
        STUDENTS_DATA[cls] = [
            {'id': str(uuid.uuid4()), 'roll_no': '1', 'name': 'Student One', 'class': cls},
            {'id': str(uuid.uuid4()), 'roll_no': '2', 'name': 'Student Two', 'class': cls},
            {'id': str(uuid.uuid4()), 'roll_no': '3', 'name': 'Student Three', 'class': cls},
        ]

# ==================== ROUTES ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid password')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard for attendance"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/admin/logout')
def admin_logout():
    """Logout from admin panel"""
    session.pop('admin_authenticated', None)
    return redirect(url_for('admin_login'))

@app.route('/api/add-student', methods=['POST'])
def add_student():
    """Add a new student"""
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json() or {}
        student_class = data.get('class')
        student_name = data.get('name')
        student_roll = data.get('roll_no')
        
        if not all([student_class, student_name, student_roll]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        if student_class not in STUDENTS_DATA:
            STUDENTS_DATA[student_class] = []
        
        student = {
            'id': str(uuid.uuid4()),
            'roll_no': student_roll,
            'name': student_name,
            'class': student_class
        }
        
        STUDENTS_DATA[student_class].append(student)
        
        # TODO: Sync to Google Sheets
        sync_to_google_sheets()
        
        return jsonify({'success': True, 'message': 'Student added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/students')
def get_students():
    """Get all students for a class"""
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    student_class = request.args.get('class', 'Class 8')
    students = STUDENTS_DATA.get(student_class, [])
    
    return jsonify({'success': True, 'students': students})

@app.route('/api/delete-student/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student"""
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        for class_name in STUDENTS_DATA:
            for i, student in enumerate(STUDENTS_DATA[class_name]):
                if student['id'] == student_id:
                    STUDENTS_DATA[class_name].pop(i)
                    sync_to_google_sheets()
                    return jsonify({'success': True})
        
        return jsonify({'success': False, 'message': 'Student not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/submit-attendance', methods=['POST'])
def submit_attendance():
    """Submit attendance for a class on a given date"""
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json() or {}
        attendance_date = data.get('date')
        selected_class = data.get('class')
        records = data.get('records', [])
        
        if not attendance_date:
            return jsonify({'success': False, 'message': 'Date is required'}), 400
        
        # Store attendance records
        for record in records:
            student_id = record.get('student_id')
            status = record.get('status')
            notes = record.get('notes', '')
            
            key = f"{attendance_date}_{selected_class}"
            if key not in ATTENDANCE_DATA:
                ATTENDANCE_DATA[key] = []
            
            ATTENDANCE_DATA[key].append({
                'student_id': student_id,
                'status': status,
                'notes': notes
            })
        
        # TODO: Sync to Google Sheets
        sync_to_google_sheets()
        
        return jsonify({'success': True, 'message': 'Attendance submitted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/attendance')
def get_attendance():
    """Fetch attendance data for a class and date"""
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    selected_class = request.args.get('class', 'Class 8')
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        key = f"{selected_date}_{selected_class}"
        attendance_records = ATTENDANCE_DATA.get(key, [])
        
        # Merge with student info
        results = []
        for record in attendance_records:
            student_id = record.get('student_id')
            # Find student info
            for class_name, students in STUDENTS_DATA.items():
                for student in students:
                    if student['id'] == student_id:
                        results.append({
                            'roll_no': student['roll_no'],
                            'student_name': student['name'],
                            'date': selected_date,
                            'status': record.get('status'),
                            'notes': record.get('notes')
                        })
        
        return jsonify({'success': True, 'records': results})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def sync_to_google_sheets():
    """Sync data to Google Sheets (TODO: Implement with actual API)"""
    # TODO: Replace with actual Google Sheets API integration
    # You'll need to:
    # 1. Authenticate with Google Sheets API using service account
    # 2. Create sheets for each class if they don't exist
    # 3. Update student and attendance data
    pass

# Initialize sample data when app starts
init_sample_data()

@app.route('/')
def home():
    """Home page - Hero section with institute intro and CTA"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page - Institute and founder details"""
    founder_data = {
        'name': 'Swaroop Kawale',
        'qualifications': 'MSc in Physics (Specialization: Solid State Physics), BSc in Physics (100/100)',
        'experience': '6 years of teaching experience',
        'subjects': 'Physics',
        'bio': 'An experienced physics educator dedicated to making physics accessible and practical. With over 6 years of teaching experience and advanced specialization in solid state physics, our founder believes in the power of practical learning over rote memorization. His unique methodology combines theoretical concepts with real-world applications, ensuring students develop both understanding and confidence.',
        'philosophy': 'Education is not about filling buckets; it is about lighting fires. Every student has the potential to excel when given the right guidance, practice, and encouragement.'
    }

    return render_template('about.html', founder=founder_data)

@app.route('/courses')
def courses():
    """Courses page - Display available classes"""
    courses_data = [
        {
            'class': 'Class 8',
            'subjects': ['Mathematics', 'Science'],
            'description': 'Foundation building course focusing on core concepts in algebra, geometry, physics, and chemistry. Interactive problem-solving sessions develop critical thinking.',
            'duration': '1 Year',
            'mode': 'Offline'
        },
        {
            'class': 'Class 9',
            'subjects': ['Mathematics', 'Science'],
            'description': 'Intermediate level course with advanced topics in algebra, trigonometry, physics, chemistry, and biology. Emphasis on application-based learning.',
            'duration': '1 Year',
            'mode': 'Offline'
        },
        {
            'class': 'Class 10',
            'subjects': ['Mathematics', 'Science'],
            'description': 'Board exam preparation course with comprehensive coverage of CBSE syllabus. Regular mock tests and doubt-clearing sessions included.',
            'duration': '1 Year',
            'mode': 'Offline'
        }
    ]

    return render_template('courses.html', courses=courses_data)

@app.route('/admissions')
def admissions():
    """Admissions page - Admission details and requirements"""
    admission_steps = [
        {'step': '01', 'title': 'Enquiry', 'description': 'Contact us via phone or visit our center to enquire about available batches.'},
        {'step': '02', 'title': 'Registration', 'description': 'Fill out the registration form with student details and submit required documents.'},
        {'step': '03', 'title': 'Enrollment', 'description': 'Complete fee payment and get enrolled in your preferred batch.'}
    ]
    additional_info = [
        'Admissions open throughout the year (subject to availability)',
        'No entrance test required',
        'Limited seats per batch to ensure personalized attention',
        'Contact us for current batch timings'
    ]
    return render_template('admissions.html', admission_steps=admission_steps, additional_info=additional_info)

@app.route('/fees')
def fees():
    """Fees page - Fee structure information"""
    fees_list = [
        {'class': 'Class 8', 'subjects': 'Mathematics & Science', 'monthly': 'Contact Us', 'annual': 'Contact Us'},
        {'class': 'Class 9', 'subjects': 'Mathematics & Science', 'monthly': 'Contact Us', 'annual': 'Contact Us'},
        {'class': 'Class 10', 'subjects': 'Mathematics & Science', 'monthly': 'Contact Us', 'annual': 'Contact Us'}
    ]
    notes = [
        'Fee structure will be shared upon enquiry',
        'Flexible payment options available',
        'Sibling discount available',
        'All course materials included in the fee'
    ]
    return render_template('fees.html', fees=fees_list, notes=notes)

@app.route('/gallery')
def gallery():
    """Gallery page - Image showcase"""
    gallery_items = [
        {'url': 'https://imagizer.imageshack.com/img922/7606/usgJRC.jpg'},
        {'url': 'https://imagizer.imageshack.com/img921/3791/y3C04k.jpg'},
        {'url': 'https://imagizer.imageshack.com/img924/9615/ea2NaK.jpg'},
        {'url': 'https://imagizer.imageshack.com/img921/7320/uyWjAu.jpg'},
        {'url': 'https://imagizer.imageshack.com/img924/7164/rHHmGA.jpg'},
        {'url': 'https://imagizer.imageshack.com/img924/8174/8IV5f4.jpg'},
        {'url': 'https://imagizer.imageshack.com/img924/790/xq6kSf.jpg'},
        {'url': 'https://imagizer.imageshack.com/img922/1155/6lvvSV.jpg'},
        {'url': 'https://imagizer.imageshack.com/img923/6659/zcwtBM.jpg'},
        {'url': 'https://imagizer.imageshack.com/img923/782/f8FTG2.jpg'},
        {'url': 'https://imagizer.imageshack.com/img924/9574/WrZoRX.jpg'},
        {'url': 'https://imagizer.imageshack.com/img922/38/xUu0Ao.jpg'},
        {'url': 'https://imagizer.imageshack.com/img924/1170/Y2aiAj.jpg'},
        {'url': 'https://imagizer.imageshack.com/img923/8562/FKIXv4.jpg'}
    ]
    return render_template('gallery.html', gallery_items=gallery_items)

@app.route('/contact')
def contact():
    """Contact page - Address and contact form"""
    contact_data = {
        'address': 'View Location on Map',
        'address_map': 'https://maps.app.goo.gl/s9szEdbYXsgZKVAE7',
        'email': 'aswathamaclasses@gmail.com'
    }

    return render_template('contact.html', data=contact_data)

@app.route('/submit-contact', methods=['POST'])
def submit_contact():
    """Handle contact form submission"""
    try:
        data = request.get_json()

        # Validate required fields
        if not all([data.get('name'), data.get('phone'), data.get('message')]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400

        # In production, this would save to database or send email
        # For now, we'll just log it
        print(f"Contact Form Submission - Name: {data['name']}, Phone: {data['phone']}, Message: {data['message']}")

        return jsonify({'success': True, 'message': 'Thank you! We will contact you soon.'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred. Please try again.'}), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    # Run Flask development server
    # For production, use Gunicorn: gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
    app.run(debug=False, host='0.0.0.0', port=5000)