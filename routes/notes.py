import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app, Response
from werkzeug.utils import secure_filename

from database import db
from database.models import Note, SystemSetting
from services.image_processing import preprocess_image
from services.ocr import extract_text_from_image
from services.subject_detector import detect_subject
from services.topic_detector import detect_topic
from services.similarity import find_duplicate_note
from services.pdf_exporter import generate_note_pdf

notes_bp = Blueprint('notes', __name__)

PREDEFINED_SUBJECTS = [
    'Java', 'Python', 'DBMS', 'Operating Systems', 'Computer Networks', 
    'Data Structures', 'Software Engineering', 'Artificial Intelligence', 
    'Machine Learning', 'Cyber Security', 'Digital Signal Processing', 'Other'
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@notes_bp.route('/upload')
def upload():
    """Upload Handwritten Notes Page"""
    return render_template('upload.html', subjects=PREDEFINED_SUBJECTS)

@notes_bp.route('/api/analyze', methods=['POST'])
def analyze_note():
    """
    AJAX Endpoint:
    1. Validates and saves uploaded image.
    2. Runs OpenCV Image Preprocessing.
    3. Runs PyTesseract OCR.
    4. Runs Subject Detection NLP.
    5. Runs Topic Detection NLP.
    6. Checks for existing Duplicate Notes.
    7. Returns JSON analysis result.
    """
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file provided in request.'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected.'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file format. Allowed formats: PNG, JPG, JPEG, WEBP, BMP.'}), 400

    try:
        # Secure unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        upload_folder = current_app.config['UPLOAD_FOLDER']
        processed_folder = current_app.config['PROCESSED_FOLDER']
        
        os.makedirs(upload_folder, exist_ok=True)
        os.makedirs(processed_folder, exist_ok=True)

        raw_path = os.path.join(upload_folder, unique_name)
        file.save(raw_path)

        # 1. Preprocessing
        processed_name = f"proc_{unique_name}"
        processed_path = os.path.join(processed_folder, processed_name)
        preprocess_image(raw_path, processed_path)

        # 2. OCR Text Extraction
        tesseract_path = SystemSetting.get_value('tesseract_path', current_app.config.get('DEFAULT_TESSERACT_PATH'))
        target_ocr_path = processed_path if os.path.exists(processed_path) else raw_path
        
        ocr_result = extract_text_from_image(target_ocr_path, configured_tesseract_path=tesseract_path)
        extracted_text = ocr_result['text']
        tesseract_installed = ocr_result['tesseract_installed']

        # 3. Subject Detection
        subject, subject_conf = detect_subject(extracted_text)

        # 4. Topic Detection
        topic = detect_topic(extracted_text, subject)

        # Overall Confidence calculation (blend of OCR confidence and NLP subject confidence)
        overall_confidence = round((ocr_result.get('confidence', 0.0) * 0.4) + (subject_conf * 0.6), 1)

        # Suggested Title from extracted text or filename
        suggested_title = file.filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title()
        if extracted_text and len(extracted_text.splitlines()) > 0:
            first_line = extracted_text.splitlines()[0].strip()
            if 3 < len(first_line) <= 50:
                suggested_title = first_line

        # 5. Duplicate Check against existing database notes
        existing_notes = Note.query.all()
        duplicate_check = find_duplicate_note(extracted_text, existing_notes, threshold=70.0)

        return jsonify({
            'success': True,
            'image_filename': unique_name,
            'processed_filename': processed_name,
            'original_filename': file.filename,
            'extracted_text': extracted_text,
            'suggested_title': suggested_title,
            'subject': subject,
            'topic': topic,
            'confidence': overall_confidence,
            'tesseract_installed': tesseract_installed,
            'ocr_warning': ocr_result['error'] if not ocr_result['success'] else None,
            'is_duplicate': duplicate_check['is_duplicate'],
            'similar_note': duplicate_check['similar_note'],
            'similarity_score': duplicate_check['similarity_score']
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error during image processing: {str(e)}'}), 500

@notes_bp.route('/notes/create', methods=['POST'])
def create_note():
    """Saves analyzed note into SQLite database"""
    title = request.form.get('title', '').strip() or 'Untitled Note'
    original_filename = request.form.get('original_filename', 'uploaded_note.jpg')
    image_filename = request.form.get('image_filename', '')
    processed_filename = request.form.get('processed_filename', '')
    extracted_text = request.form.get('extracted_text', '').strip()
    subject = request.form.get('subject', 'Other').strip()
    topic = request.form.get('topic', 'General').strip()
    try:
        confidence = float(request.form.get('confidence', 0.0))
    except ValueError:
        confidence = 0.0

    if not image_filename:
        flash('Cannot save note without image file.', 'danger')
        return redirect(url_for('notes.upload'))

    new_note = Note(
        title=title,
        original_filename=original_filename,
        image_path=image_filename,
        processed_image_path=processed_filename,
        extracted_text=extracted_text,
        subject=subject,
        topic=topic,
        confidence=confidence,
        is_demo=False
    )

    db.session.add(new_note)
    db.session.commit()

    flash('Note saved successfully!', 'success')
    return redirect(url_for('notes.note_detail', note_id=new_note.id))

@notes_bp.route('/notes')
def list_notes():
    """All Notes page with live search, subject filter, topic filter, and sorting"""
    search_query = request.args.get('search', '').strip()
    subject_filter = request.args.get('subject', '').strip()
    topic_filter = request.args.get('topic', '').strip()
    sort_by = request.args.get('sort', 'date_desc').strip()

    query = Note.query

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (Note.title.ilike(search_pattern)) |
            (Note.extracted_text.ilike(search_pattern)) |
            (Note.subject.ilike(search_pattern)) |
            (Note.topic.ilike(search_pattern))
        )

    if subject_filter and subject_filter != 'All':
        query = query.filter(Note.subject == subject_filter)

    if topic_filter and topic_filter != 'All':
        query = query.filter(Note.topic == topic_filter)

    # Sorting
    if sort_by == 'date_asc':
        query = query.order_by(Note.created_at.asc())
    elif sort_by == 'title_asc':
        query = query.order_by(Note.title.asc())
    elif sort_by == 'confidence_desc':
        query = query.order_by(Note.confidence.desc())
    else: # date_desc
        query = query.order_by(Note.created_at.desc())

    notes = query.all()

    # Get unique topics list for filter dropdown
    available_topics = db.session.query(Note.topic).distinct().all()
    topics_list = [t[0] for t in available_topics if t[0]]

    return render_template(
        'notes.html',
        notes=notes,
        subjects=PREDEFINED_SUBJECTS,
        available_topics=topics_list,
        selected_search=search_query,
        selected_subject=subject_filter,
        selected_topic=topic_filter,
        selected_sort=sort_by
    )

@notes_bp.route('/notes/<int:note_id>')
def note_detail(note_id):
    """Note Detail page"""
    note = Note.query.get_or_404(note_id)
    return render_template('note_detail.html', note=note)

@notes_bp.route('/notes/<int:note_id>/edit')
def edit_note_form(note_id):
    """Form to edit note details"""
    note = Note.query.get_or_404(note_id)
    return render_template('edit_note.html', note=note, subjects=PREDEFINED_SUBJECTS)

@notes_bp.route('/notes/<int:note_id>/update', methods=['POST'])
def update_note(note_id):
    """Processes note update form"""
    note = Note.query.get_or_404(note_id)
    
    note.title = request.form.get('title', '').strip() or note.title
    note.extracted_text = request.form.get('extracted_text', '').strip()
    note.subject = request.form.get('subject', 'Other').strip()
    note.topic = request.form.get('topic', 'General').strip()

    db.session.commit()
    flash('Note updated successfully!', 'success')
    return redirect(url_for('notes.note_detail', note_id=note.id))

@notes_bp.route('/notes/<int:note_id>/delete', methods=['POST'])
def delete_note(note_id):
    """Deletes note and attached image files from server"""
    note = Note.query.get_or_404(note_id)

    # Delete physical image files if not demo file
    if not note.is_demo and note.image_path:
        raw_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], note.image_path)
        if os.path.exists(raw_full_path):
            try:
                os.remove(raw_full_path)
            except Exception:
                pass

        if note.processed_image_path:
            proc_full_path = os.path.join(current_app.config['PROCESSED_FOLDER'], note.processed_image_path)
            if os.path.exists(proc_full_path):
                try:
                    os.remove(proc_full_path)
                except Exception:
                    pass

    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully.', 'info')
    return redirect(url_for('notes.list_notes'))

@notes_bp.route('/subjects')
def subjects():
    """Subjects overview page listing cards with note count"""
    subject_counts = []
    for subj in PREDEFINED_SUBJECTS:
        count = Note.query.filter_by(subject=subj).count()
        topics_count = db.session.query(Note.topic).filter_by(subject=subj).distinct().count()
        subject_counts.append({
            'name': subj,
            'count': count,
            'topics_count': topics_count
        })

    return render_template('subjects.html', subject_counts=subject_counts)

@notes_bp.route('/subjects/<subject_name>')
def subject_notes(subject_name):
    """Shows all notes under a specific subject grouped visually by Topic"""
    notes = Note.query.filter_by(subject=subject_name).order_by(Note.topic, Note.created_at.desc()).all()

    # Group notes by topic
    grouped_topics = {}
    for note in notes:
        topic_key = note.topic or 'General'
        if topic_key not in grouped_topics:
            grouped_topics[topic_key] = []
        grouped_topics[topic_key].append(note)

    return render_template('subject_notes.html', subject_name=subject_name, grouped_topics=grouped_topics, total_notes=len(notes))

@notes_bp.route('/search')
def search():
    """Global search route"""
    query_str = request.args.get('q', '').strip()
    results = []

    if query_str:
        pattern = f"%{query_str}%"
        results = Note.query.filter(
            (Note.title.ilike(pattern)) |
            (Note.extracted_text.ilike(pattern)) |
            (Note.subject.ilike(pattern)) |
            (Note.topic.ilike(pattern))
        ).order_by(Note.created_at.desc()).all()

    return render_template('search.html', query=query_str, results=results)

@notes_bp.route('/notes/<int:note_id>/download/txt')
def download_txt(note_id):
    """Download Note as TXT File"""
    note = Note.query.get_or_404(note_id)

    created_str = note.created_at.strftime('%Y-%m-%d %H:%M') if hasattr(note.created_at, 'strftime') else str(note.created_at)

    content = f"""==================================================
NOTELENS - SMART HANDWRITTEN NOTES ORGANIZER
==================================================

Title: {note.title}
Subject: {note.subject}
Topic: {note.topic}
Confidence: {note.confidence}%
Created Date: {created_str}

--------------------------------------------------
EXTRACTED HANDWRITTEN TEXT:
--------------------------------------------------

{note.extracted_text}

==================================================
Generated by NoteLens
"""
    filename = f"{secure_filename(note.title or 'note')}_NoteLens.txt"
    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

@notes_bp.route('/notes/<int:note_id>/download/pdf')
def download_pdf(note_id):
    """Download Note as formatted PDF Document"""
    note = Note.query.get_or_404(note_id)
    pdf_buffer = generate_note_pdf(note)
    filename = f"{secure_filename(note.title or 'note')}_NoteLens.pdf"
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )
