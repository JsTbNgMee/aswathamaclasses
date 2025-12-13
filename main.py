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
        'name': 'Swaroop Kawale',
        'qualifications': 'B.Tech in Engineering, M.Tech (Advanced Computing)',
        'experience': '12+ years of teaching experience',
        'subjects': 'Mathematics & Science',
        'bio': 'Swaroop Kawale is a visionary educator dedicated to making mathematics and science accessible and practical. With over a decade of experience in classroom instruction and curriculum development, Swaroop believes in the power of practical learning over rote memorization. His unique methodology combines theoretical concepts with real-world applications, ensuring students develop both understanding and confidence.',
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
    admissions_data = {
        'title': 'Join ASWATHAMA CLASSES',
        'intro': 'We believe in nurturing young minds through practical learning and dedicated mentorship. Our admission process is simple and transparent.',
        'eligibility': 'Placeholder - Eligibility criteria will be added soon',
        'process': 'Placeholder - Admission process details will be added soon',
        'documents': 'Placeholder - Required documents list will be added soon',
        'contact_info': 'For admission queries, please contact us directly.'
    }

    return render_template('admissions.html', data=admissions_data)

@app.route('/fees')
def fees():
    """Fees page - Fee structure information"""
    fees_data = {
        'title': 'Fee Structure',
        'intro': 'Transparent and affordable fee structure designed to be accessible to all.',
        'note': 'Detailed fee structure with payment options will be updated soon.',
        'classes': [
            {'name': 'Class 8', 'amount': 'Coming Soon'},
            {'name': 'Class 9', 'amount': 'Coming Soon'},
            {'name': 'Class 10', 'amount': 'Coming Soon'}
        ],
        'benefits': [
            'Lifetime access to course materials',
            'Regular doubt-clearing sessions',
            'Monthly performance tracking',
            'Flexible payment options available'
        ]
    }

    return render_template('fees.html', data=fees_data)

@app.route('/gallery')
def gallery():
    """Gallery page - Image showcase"""
    gallery_data = {
        'title': 'ASWATHAMA CLASSES Gallery',
        'intro': 'Experience our state-of-the-art learning environment',
        'images': [
            {'id': 1, 'alt': 'Classroom Environment'},
            {'id': 2, 'alt': 'Study Materials'},
            {'id': 3, 'alt': 'Student Interaction'},
            {'id': 4, 'alt': 'Teaching Session'},
            {'id': 5, 'alt': 'Library Resources'},
            {'id': 6, 'alt': 'Student Discussion'}
        ]
    }

    return render_template('gallery.html', data=gallery_data)

@app.route('/contact')
def contact():
    """Contact page - Address and contact form"""
    contact_data = {
        'address': 'Address placeholder - Will be added soon',
        'phone': 'Phone placeholder - Will be added soon',
        'email': 'email@placeholder.com'
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
    # For production, use Gunicorn or similar WSGI server
    app.run(debug=True, host='0.0.0.0', port=5000)