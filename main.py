"""
ASWATHAMA CLASSES - Professional Coaching Institute Website
Backend: Flask
Author: Senior Full-Stack Developer
Description: A premium, minimalist coaching institute website with black & white theme
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
import os
from youtube_service import yt_service
from student_data import authenticate_student, get_student

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'aswathama-classes-secret-key-secure'

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

@app.route('/instagram')
def instagram():
    """Instagram page - Link to Instagram profile"""
    return render_template('instagram.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    """Student login page"""
    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        password = request.form.get('password', '').strip()
        
        from student_data import authenticate_student
        student = authenticate_student(student_id, password)
        
        if student:
            session['student_id'] = student['id']
            session['student_name'] = student['name']
            return redirect(url_for('student_dashboard'))
        else:
            return render_template('student_login.html', error='Invalid Student ID or Password')
    
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
    from student_data import get_all_students
    return render_template('teacher_dashboard.html', students=get_all_students())

@app.route('/teacher/add-student', methods=['POST'])
def teacher_add_student():
    if not session.get('teacher_logged_in'): return redirect(url_for('teacher_login'))
    from student_data import add_student
    student_data = {
        'id': request.form.get('id'),
        'name': request.form.get('name'),
        'password': request.form.get('password'),
        'class': request.form.get('class'),
        'email': '', 'phone': '', 'enrollment_date': datetime.now().strftime('%Y-%m-%d'),
        'marks': {'Mathematics': 0, 'Science': 0, 'Physics': 0, 'Chemistry': 0},
        'attendance': {'total_classes': 0, 'attended': 0, 'percentage': 0},
        'progress': {'completion': 0, 'status': 'New', 'performance': 'N/A'}
    }
    add_student(student_data)
    return redirect(url_for('teacher_dashboard'))

@app.route('/teacher/edit-student/<student_id>', methods=['GET', 'POST'])
def teacher_edit_student(student_id):
    if not session.get('teacher_logged_in'): return redirect(url_for('teacher_login'))
    from student_data import get_student, update_student
    student = get_student(student_id)
    if request.method == 'POST':
        updated_data = student.copy()
        updated_data['name'] = request.form.get('name')
        updated_data['class'] = request.form.get('class')
        updated_data['email'] = request.form.get('email')
        updated_data['phone'] = request.form.get('phone')
        
        # Update Marks
        for sub in updated_data['marks']:
            updated_data['marks'][sub] = int(request.form.get(f'mark_{sub}', 0))
            
        # Update Attendance
        att = updated_data['attendance']
        att['attended'] = int(request.form.get('attended', 0))
        att['total_classes'] = int(request.form.get('total_classes', 0))
        att['percentage'] = (att['attended'] / att['total_classes'] * 100) if att['total_classes'] > 0 else 0
        
        # Update Progress
        prog = updated_data['progress']
        prog['completion'] = int(request.form.get('completion', 0))
        prog['status'] = request.form.get('status')
        
        update_student(student_id, updated_data)
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('teacher_edit.html', student=student)

@app.route('/teacher/delete-student/<student_id>', methods=['POST'])
def teacher_delete_student(student_id):
    if not session.get('teacher_logged_in'): return redirect(url_for('teacher_login'))
    from student_data import delete_student
    delete_student(student_id)
    return redirect(url_for('teacher_dashboard'))

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
