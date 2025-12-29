"""
ASHWATHAMA CLASSES - Professional Coaching Institute Website
Backend: Flask
Author: Senior Full-Stack Developer
Description: A premium, minimalist coaching institute website with black & white theme
"""

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
from flask_compress import Compress
from datetime import datetime, timedelta
import os
from youtube_service import yt_service
from google_sheets_direct import init_sheets_service, get_sheets_service

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'aswathama-classes-secret-key-secure'

# Enable Gzip compression
Compress(app)

# Initialize Google Sheets service
init_sheets_service(app)

# Helper functions for student operations
def authenticate_student(student_id, password):
    """Authenticate student via Google Sheets"""
    service = get_sheets_service()
    if not service:
        return None
    return service.authenticate_student(student_id, password)

def get_student(student_id):
    """Get student data from Google Sheets"""
    service = get_sheets_service()
    if not service:
        return None
    student = service.get_student(student_id)
    if student and isinstance(student, dict):
        return student
    return None

# ==================== ROUTES ====================

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

@app.route('/youtube')
def youtube():
    """YouTube page - Display latest videos"""
    videos = yt_service.get_latest_videos(max_results=12) if yt_service.is_configured() else []
    return render_template('youtube.html', videos=videos)

@app.route('/leaderboard')
def leaderboard():
    """Leaderboard page - Display toppers for each test"""
    service = get_sheets_service()
    data = service.get_leaderboard() if service else []
    return render_template('leaderboard.html', leaderboard_data=data)

@app.route('/instagram')
def instagram():
    """Instagram page - Link to Instagram profile"""
    return render_template('instagram.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    """Student login page"""
    if request.method == 'POST':
        username = str(request.form.get('student_id', '')).strip()
        password = str(request.form.get('password', '')).strip()
        
        service = get_sheets_service()
        student = service.authenticate_student(username, password) if service else None
        
        if student:
            # Crucial: ID is the key for fetching data later
            session['student_id'] = str(student.get('id', username)).strip()
            session['student_name'] = student.get('name', username)
            return redirect(url_for('student_dashboard'))
        else:
            return render_template('student_login.html', error='Invalid Student Name/ID or Password')
    
    return render_template('student_login.html')

@app.route('/student/dashboard')
def student_dashboard():
    """Student dashboard - view grades, attendance, progress"""
    if 'student_id' not in session:
        return redirect(url_for('student_login'))
    
    student = get_student(session['student_id'])
    
    if not student:
        session.clear()
        return redirect(url_for('student_login'))
    
    return render_template('student_dashboard.html', student=student)

@app.route('/student/logout')
def student_logout():
    """Logout student"""
    session.clear()
    return redirect(url_for('student_login'))

# ==================== TEACHER ROUTES ====================

@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'aswathama2024': # Teacher credentials
            session['teacher_logged_in'] = True
            return redirect(url_for('teacher_dashboard'))
        return render_template('teacher_login.html', error='Invalid credentials')
    return render_template('teacher_login.html')

@app.route('/teacher/dashboard')
def teacher_dashboard():
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher_login'))
    service = get_sheets_service()
    students = service.get_all_students() if service else []
    return render_template('teacher_dashboard.html', students=students)

@app.route('/teacher/add-student', methods=['POST'])
def teacher_add_student():
    if not session.get('teacher_logged_in'): return redirect(url_for('teacher_login'))
    service = get_sheets_service()
    student_data = {
        'id': request.form.get('id'),
        'name': request.form.get('name'),
        'password': request.form.get('password'),
        'student_class': request.form.get('class'),
        'email': '', 'phone': '', 'enrollment_date': datetime.now().strftime('%Y-%m-%d'),
        'tests_json': '[]', 'attendance_log_json': '[]', 'progress_json': '{"completion": 0, "status": "New", "performance": "N/A"}'
    }
    if service:
        service.add_student(student_data)
        # Sync to Auth sheet
        service.sync_auth_record(student_data.get('name'), student_data.get('password'), student_data.get('id'))
    return redirect(url_for('teacher_dashboard'))

@app.route('/teacher/edit-student/<student_id>', methods=['GET', 'POST'])
def teacher_edit_student(student_id):
    if not session.get('teacher_logged_in'): return redirect(url_for('teacher_login'))
    service = get_sheets_service()
    student = get_student(student_id) if service else None
    if request.method == 'POST':
        updated_data = student.copy() if student else {}
        updated_data['name'] = request.form.get('name') or ''
        updated_data['student_class'] = request.form.get('class') or ''
        updated_data['email'] = request.form.get('email') or ''
        updated_data['phone'] = request.form.get('phone') or ''
        
        # Update Weekly Tests
        names = request.form.getlist('test_name[]') or []
        dates = request.form.getlist('test_date[]') or []
        marks = request.form.getlist('test_marks[]') or []
        totals = request.form.getlist('test_total[]') or []
        tests = []
        for i in range(len(names)):
            if names[i]:
                tests.append({
                    'name': names[i],
                    'date': dates[i],
                    'marks': int(marks[i] or 0),
                    'total': int(totals[i] or 0)
                })
        updated_data['tests'] = tests

        # Update Attendance Log
        att_dates = request.form.getlist('att_date[]') or []
        att_status = request.form.getlist('att_status[]') or []
        attendance_log = []
        for i in range(len(att_dates)):
            if att_dates[i]:
                attendance_log.append({
                    'date': att_dates[i],
                    'status': att_status[i]
                })
        updated_data['attendance_log'] = attendance_log
        
        # Ensure password is preserved
        if 'password' not in updated_data and student and 'password' in student:
            updated_data['password'] = student['password']
        
        if service:
            service.update_student(student_id, updated_data)
            # Sync to Auth sheet
            service.sync_auth_record(updated_data.get('name'), updated_data.get('password'), student_id)
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('teacher_edit.html', student=student)

@app.route('/teacher/delete-student/<student_id>', methods=['POST'])
def teacher_delete_student(student_id):
    if not session.get('teacher_logged_in'): return redirect(url_for('teacher_login'))
    service = get_sheets_service()
    if service:
        service.delete_student(student_id)
    return redirect(url_for('teacher_dashboard'))

@app.route('/teacher/attendance', methods=['GET', 'POST'])
def teacher_attendance():
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher_login'))
    
    service = get_sheets_service()
    students = service.get_all_students() if service else []
    
    if request.method == 'POST':
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        absent_ids = request.form.getlist('absent_students')
        
        attendance_map = {}
        absentee_names = []
        for student in students:
            s_id = student.get('id')
            status = 'Absent' if s_id in absent_ids else 'Present'
            attendance_map[s_id] = status
            if status == 'Absent':
                absentee_names.append(student.get('name', s_id))
        
        if service:
            service.batch_update_attendance(attendance_map, date)
        
        # Show success message with absentee list
        msg = f"Attendance submitted for {date}. Absentees: {', '.join(absentee_names) if absentee_names else 'None'}"
        return render_template('teacher_attendance.html', students=students, today=date, success=msg, absentees=absentee_names)

    return render_template('teacher_attendance.html', students=students, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/teacher/tests', methods=['GET', 'POST'])
def teacher_tests():
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher_login'))
    
    service = get_sheets_service()
    students = service.get_all_students() if service else []
    
    if request.method == 'POST':
        test_name = request.form.get('test_name')
        test_date = request.form.get('test_date')
        total_marks = request.form.get('total_marks')
        
        test_data = {}
        for student in students:
            s_id = student.get('id')
            marks = request.form.get(f'marks_{s_id}')
            if marks is not None and marks.strip() != '':
                test_data[s_id] = marks
        
        if service and test_data:
            service.batch_add_tests(test_data, test_name, test_date, total_marks)
            msg = f"Successfully added marks for '{test_name}' on {test_date}."
            return render_template('teacher_tests.html', students=students, today=test_date, success=msg)

    return render_template('teacher_tests.html', students=students, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/teacher/logout')
def teacher_logout():
    session.pop('teacher_logged_in', None)
    return redirect(url_for('teacher_login'))

@app.route('/contact')
def contact():
    """Contact page - Address and contact form"""
    contact_data = {
        'email': 'aswathamaclasses@gmail.com',
        'branches': [
            {
                'name': 'Main Branch',
                'address': 'View Location on Map',
                'address_map': 'https://maps.app.goo.gl/s9szEdbYXsgZKVAE7',
                'phone': '+91 90193 74771'
            },
            {
                'name': 'Second Branch',
                'address': 'Coming Soon',
                'address_map': '#',
                'phone': 'Contact us for details'
            }
        ]
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

@app.after_request
def add_security_headers(response):
    """Add security headers to every response"""
    # Content Security Policy
    # We allow scripts from self, and certain trusted domains for embeds/styles
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "frame-src 'self' https://drive.google.com https://www.google.com https://www.youtube.com; "
        "connect-src 'self';"
    )
    response.headers['Content-Security-Policy'] = csp
    
    # HSTS - 1 year
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    
    # Clickjacking protection
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # XSS Protection
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Cross-Origin Opener Policy
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response

@app.route('/robots.txt')
def robots():
    """Serve robots.txt dynamically"""
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.url_root.rstrip('/')}/sitemap.xml"
    ]
    response = make_response("\n".join(lines))
    response.headers["Content-Type"] = "text/plain"
    return response

@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml dynamically"""
    pages = []
    # Use today's date for lastmod to ensure search engines see it as fresh
    today = datetime.now().date().isoformat()
    
    # List of static routes to include in sitemap
    static_routes = [
        ('home', 1.0, 'daily'),
        ('about', 0.8, 'monthly'),
        ('courses', 0.9, 'weekly'),
        ('admissions', 0.9, 'weekly'),
        ('fees', 0.7, 'monthly'),
        ('gallery', 0.7, 'weekly'),
        ('youtube', 0.8, 'weekly'),
        ('leaderboard', 0.9, 'daily'),
        ('contact', 0.8, 'monthly')
    ]
    
    for rule, priority, changefreq in static_routes:
        try:
            pages.append({
                "loc": url_for(rule, _external=True),
                "lastmod": today,
                "priority": priority,
                "changefreq": changefreq
            })
        except Exception as e:
            print(f"Error generating URL for {rule}: {e}")
        
    sitemap_xml = render_template('sitemap.xml', urls=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response

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
