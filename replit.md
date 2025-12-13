# ASWATHAMA CLASSES Website

A professional, minimalist coaching institute website built with Flask and Jinja2 templates.

## Overview
- **Institute**: ASWATHAMA CLASSES
- **Tagline**: Learn Practically
- **Founder**: Swaroop Kawale
- **Subjects**: Mathematics & Science
- **Classes**: 8, 9, 10
- **Mode**: Offline only

## Design Theme
- White background (#FFFFFF)
- Black text (#000000)
- Clean, modern, premium aesthetic
- Mobile-first responsive design
- No gradients, minimal colors
- Elegant hover effects

## Pages
1. **Home** (`/`) - Hero section with institute intro and CTAs
2. **About** (`/about`) - Founder profile and mission statement
3. **Courses** (`/courses`) - Class 8, 9, 10 course cards
4. **Admissions** (`/admissions`) - 3-step admission process
5. **Fees** (`/fees`) - Fee structure table (placeholders)
6. **Gallery** (`/gallery`) - Image gallery (placeholders)
7. **Contact** (`/contact`) - Contact info + working contact form

## Tech Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Templates**: Jinja2 with base template inheritance

## File Structure
```
main.py                    # Flask routes and backend logic
static/css/style.css       # All styling
templates/
├── base.html              # Base template (navbar, footer)
├── index.html             # Home page
├── about.html             # About page
├── courses.html           # Courses page
├── admissions.html        # Admissions page
├── fees.html              # Fees page
├── gallery.html           # Gallery page
└── contact.html           # Contact page with form
```

## Running the App
The Flask server runs on `0.0.0.0:5000` with:
```bash
python main.py
```

## Features
- Responsive mobile navigation with hamburger menu
- SEO-friendly HTML meta tags
- Working contact form with JSON API
- Production-ready CSS with CSS variables
- Clean, maintainable code structure

## Placeholders to Update
- Contact address and phone number
- Fee amounts (currently "Contact Us")
- Gallery images (currently placeholder boxes)
- Email address
