"""
ASWATHAMA CLASSES - Professional Coaching Institute Website
Backend: Flask
Author: Senior Full-Stack Developer
Description: A premium, minimalist coaching institute website with black & white theme
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'aswathama-classes-secret-key'

# ==================== ROUTES ====================

@app.route('/')
def home():
    """Home page - Hero section with institute intro and CTA"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page - Institute and founder details"""
    founder_data = {
        'name': 'Sir',
        'qualifications': 'MSc in Physics (Specialization: Solid State Physics), BSc in Physics (100/100)',
        'experience': '6+ years of teaching experience',
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
        {'title': 'Classroom', 'description': 'Our spacious and well-equipped classroom', 'image': 'https://drive.google.com/uc?export=view&id=1AhZqPE8KTMDTAjoX4X4PwZIE7G7KpnQ2'},
        {'title': 'Teaching Session', 'description': 'Interactive teaching in progress', 'image': 'https://drive.google.com/uc?export=view&id=1r7c6sLzjJBYFTsfAimW3atAWGNt3VATr'},
        {'title': 'Study Materials', 'description': 'Comprehensive study materials', 'image': 'https://drive.google.com/uc?export=view&id=1sKZbNIasgK5Ke-Rwm7Ty49_0ELtnXN8O'},
        {'title': 'Student Discussion', 'description': 'Collaborative learning sessions', 'image': 'https://drive.google.com/uc?export=view&id=1tivdSu8MRPeCCIrgdaBccf2YHaPaJKDm'},
        {'title': 'Problem Solving', 'description': 'Hands-on problem solving activities', 'image': 'https://drive.google.com/uc?export=view&id=1c6bAiX-h_xz03N-VCpMB_2FPa4cZa98b'},
        {'title': 'Exam Preparation', 'description': 'Focused exam preparation sessions', 'image': 'https://drive.google.com/uc?export=view&id=1mQDGNiKwex-gOcqwYXDIHLJVt6w_LtPI'}
    ]
    return render_template('gallery.html', gallery_items=gallery_items)

@app.route('/contact')
def contact():
    """Contact page - Address and contact form"""
    contact_data = {
        'address': 'Address placeholder - Will be added soon',
        'phone': 'Phone placeholder - Will be added soon',
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