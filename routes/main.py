from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from database import db
from database.models import Note, SystemSetting
from services.ocr import is_tesseract_available, get_tesseract_cmd
import os
import shutil

main_bp = Blueprint('main', __name__)

PREDEFINED_SUBJECTS = [
    'Java', 'Python', 'DBMS', 'Operating Systems', 'Computer Networks', 
    'Data Structures', 'Software Engineering', 'Artificial Intelligence', 
    'Machine Learning', 'Cyber Security', 'Digital Signal Processing', 'Other'
]

@main_bp.route('/')
def index():
    """Modern Landing Page"""
    total_notes = Note.query.count()
    return render_template('index.html', total_notes=total_notes)

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard page displaying counters, recent notes, subject statistics and Chart.js integration"""
    total_notes = Note.query.count()
    total_subjects = db.session.query(Note.subject).distinct().count()
    total_topics = db.session.query(Note.topic).distinct().count()

    recent_notes = Note.query.order_by(Note.created_at.desc()).limit(5).all()

    # Calculate count per subject for cards and chart
    subject_counts = {}
    for subj in PREDEFINED_SUBJECTS:
        count = Note.query.filter_by(subject=subj).count()
        subject_counts[subj] = count

    # Add any extra custom subjects found in database
    extra_subjects = db.session.query(Note.subject).filter(~Note.subject.in_(PREDEFINED_SUBJECTS)).distinct().all()
    for (subj,) in extra_subjects:
        if subj:
            subject_counts[subj] = Note.query.filter_by(subject=subj).count()

    # Chart data
    chart_labels = [s for s, c in subject_counts.items() if c > 0]
    chart_data = [c for s, c in subject_counts.items() if c > 0]

    # Fallback chart preview if database is completely empty
    if not chart_labels:
        chart_labels = ['Operating Systems', 'Java', 'DBMS', 'Computer Networks', 'Python']
        chart_data = [0, 0, 0, 0, 0]

    return render_template(
        'dashboard.html',
        total_notes=total_notes,
        total_subjects=total_subjects,
        total_topics=total_topics,
        recent_notes=recent_notes,
        subject_counts=subject_counts,
        chart_labels=chart_labels,
        chart_data=chart_data,
        all_subjects=PREDEFINED_SUBJECTS
    )

@main_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """Settings page for configuring Tesseract OCR path and system parameters"""
    current_path = SystemSetting.get_value('tesseract_path', current_app.config.get('DEFAULT_TESSERACT_PATH'))
    
    if request.method == 'POST':
        new_path = request.form.get('tesseract_path', '').strip()
        SystemSetting.set_value('tesseract_path', new_path)
        flash('Settings saved successfully.', 'success')
        return redirect(url_for('main.settings'))

    tesseract_installed = is_tesseract_available(current_path)
    resolved_binary = get_tesseract_cmd(current_path)

    return render_template(
        'settings.html',
        tesseract_path=current_path or '',
        tesseract_installed=tesseract_installed,
        resolved_binary=resolved_binary
    )

@main_bp.route('/demo/load', methods=['POST'])
def load_demo_data():
    """Seeds sample notes for Java, DBMS, OS, Networks, and Python so dashboard is not empty"""
    try:
        # Check if demo notes already exist
        existing_demo = Note.query.filter_by(is_demo=True).count()
        if existing_demo > 0:
            flash('Demo data is already loaded.', 'info')
            return redirect(url_for('main.dashboard'))

        # Copy sample placeholder images if needed
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)

        demo_notes = [
            {
                'title': 'Deadlock & Resource Allocation Graph',
                'original_filename': 'os_deadlock_notes.jpg',
                'image_path': 'demo_os.png',
                'subject': 'Operating Systems',
                'topic': 'Deadlock',
                'confidence': 94.5,
                'extracted_text': 'Deadlock occurs when two or more processes wait indefinitely for resources held by each other.\nFour Necessary Conditions:\n1. Mutual Exclusion\n2. Hold and Wait\n3. No Preemption\n4. Circular Wait\nBankers Algorithm is used for deadlock avoidance using safe sequence.'
            },
            {
                'title': 'Core Java Object-Oriented Principles',
                'original_filename': 'java_oop_concepts.jpg',
                'image_path': 'demo_java.png',
                'subject': 'Java',
                'topic': 'OOP (Object Oriented Programming)',
                'confidence': 96.0,
                'extracted_text': 'class, object, inheritance, polymorphism, encapsulation\nKey concepts in Java:\n- Inheritance: extends parent class attributes & methods\n- Polymorphism: method overloading and method overriding\n- Encapsulation: wrapping data members and methods using private access modifiers'
            },
            {
                'title': 'SQL Normalization Rules (1NF to BCNF)',
                'original_filename': 'dbms_normalization.jpg',
                'image_path': 'demo_dbms.png',
                'subject': 'DBMS',
                'topic': 'Normalization',
                'confidence': 92.0,
                'extracted_text': 'Database Normalization minimizes data redundancy and prevents anomalies.\n1NF: Atomic attributes, no repeating groups\n2NF: 1NF + no partial dependency on primary key\n3NF: 2NF + no transitive dependency\nBCNF: Strict 3NF where every determinant is a super key.'
            },
            {
                'title': 'TCP vs UDP Transport Protocol Comparison',
                'original_filename': 'networks_tcp_udp.jpg',
                'image_path': 'demo_networks.png',
                'subject': 'Computer Networks',
                'topic': 'Transport Protocols (TCP/UDP)',
                'confidence': 89.5,
                'extracted_text': 'OSI Model Transport Layer Protocols:\nTCP (Transmission Control Protocol):\n- Connection-oriented with 3-way handshake (SYN, SYN-ACK, ACK)\n- Reliable, flow control & congestion control\nUDP (User Datagram Protocol):\n- Connectionless, low latency, unreliable datagram stream'
            },
            {
                'title': 'Python List Comprehensions & Decorators',
                'original_filename': 'python_syntax_cheat.jpg',
                'image_path': 'demo_python.png',
                'subject': 'Python',
                'topic': 'Functions & Modules',
                'confidence': 95.2,
                'extracted_text': "Python Syntax Highlights:\n# List comprehension\nsquares = [x**2 for x in range(10) if x % 2 == 0]\n\n# Decorator pattern\ndef my_decorator(func):\n    def wrapper(*args, **kwargs):\n        print(\"Executing function...\")\n        return func(*args, **kwargs)\n    return wrapper"
            }
        ]

        for item in demo_notes:
            n = Note(
                title=item['title'],
                original_filename=item['original_filename'],
                image_path=item['image_path'],
                subject=item['subject'],
                topic=item['topic'],
                confidence=item['confidence'],
                extracted_text=item['extracted_text'],
                is_demo=True
            )
            db.session.add(n)
        
        db.session.commit()
        flash('Successfully loaded realistic demo notes!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to load demo data: {str(e)}', 'danger')

    return redirect(url_for('main.dashboard'))

@main_bp.route('/demo/clear', methods=['POST'])
def clear_demo_data():
    """Clears demo notes from database"""
    try:
        deleted_count = Note.query.filter_by(is_demo=True).delete()
        db.session.commit()
        flash(f'Removed {deleted_count} demo notes.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to clear demo notes: {str(e)}', 'danger')

    return redirect(url_for('main.dashboard'))
