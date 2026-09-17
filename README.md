# NoteLens – Smart Handwritten Notes Organizer

NoteLens is a smart, full-stack handwritten notes management system designed specifically for college and university students. Upload photographs or scans of handwritten notes, and NoteLens automatically cleans the image, extracts handwritten text via OCR, classifies the academic subject and topic using lightweight local NLP algorithms, detects potential duplicates, and organizes your study materials in a searchable local dashboard.

---

## 🚀 Features

- **Modern Responsive SaaS Landing Page & Dashboard**: Clean UI with dark/light mode toggle, Chart.js analytics ("Notes per Subject"), and instant search.
- **Image Preprocessing Pipeline**: Grayscale conversion, bilateral noise reduction, CLAHE contrast enhancement, deskewing, and adaptive thresholding using OpenCV & Pillow.
- **Tesseract OCR Integration**: Automatic text extraction with robust error handling and Windows path configuration settings.
- **Local Rule-Based Subject Detection**: Classifies notes into 12 college CS subjects (*Operating Systems, Java, DBMS, Computer Networks, Python, Data Structures, Software Engineering, Artificial Intelligence, Machine Learning, Cyber Security, Digital Signal Processing, Other*) with confidence scoring.
- **Topic Classifier**: Identifies specific course topics (e.g., *Deadlock, Normalization, TCP/UDP, Inheritance, Sorting*) based on keyword frequency.
- **Duplicate Note Detection**: Prevents duplicate note creation using string similarity scoring.
- **Export Options**: Download any note as a formatted `.txt` file or a styled `.pdf` document (built with ReportLab).
- **Offline & Zero Paid API Dependency**: Runs completely locally without requiring paid AI services or external subscriptions.

---

## 🛠 Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Bootstrap Icons, Chart.js
- **Backend**: Python 3.12, Flask 3.1, Werkzeug
- **Database**: SQLite, Flask-SQLAlchemy 3.1
- **OCR Engine**: Tesseract OCR, `pytesseract`
- **Image Processing**: OpenCV (`opencv-python`), Pillow
- **Document Generation**: ReportLab

---

## 📁 Project Structure

```
NoteLens/
│
├── app.py                  # Main Flask application entry point
├── config.py               # Configuration & default settings
├── requirements.txt        # Python dependency manifest
├── README.md               # Detailed documentation
├── .gitignore              # Git ignore configuration
│
├── database/
│   ├── __init__.py
│   └── models.py           # Note and SystemSetting SQLAlchemy models
│
├── services/
│   ├── __init__.py
│   ├── image_processing.py # OpenCV & Pillow preprocessing pipeline
│   ├── ocr.py              # Pytesseract wrapper and fallback error handler
│   ├── subject_detector.py # Keyword-driven local NLP subject classifier
│   ├── topic_detector.py   # Topic extraction engine
│   ├── similarity.py       # Duplicate detection engine
│   └── pdf_exporter.py     # ReportLab PDF generator
│
├── routes/
│   ├── __init__.py
│   ├── main.py             # Landing page, dashboard, settings, demo data routes
│   └── notes.py            # Upload, list, edit, delete, export & search routes
│
├── templates/
│   ├── base.html           # Master layout with navbar, sidebar, theme switcher
│   ├── index.html          # Modern landing page
│   ├── dashboard.html      # Analytics dashboard with Chart.js
│   ├── upload.html         # Drag & drop upload & analysis page
│   ├── notes.html          # All Notes gallery with live search & filters
│   ├── note_detail.html    # Detailed note view with image preview
│   ├── edit_note.html      # Note editor
│   ├── subjects.html       # Subject directory
│   ├── subject_notes.html  # Notes grouped by topic
│   ├── search.html         # Global search results
│   ├── settings.html       # Tesseract path configuration
│   ├── 404.html            # Custom 404 error page
│   └── 500.html            # Custom 500 error page
│
├── static/
│   ├── css/
│   │   └── style.css       # Custom styles, light/dark themes, responsive layout
│   └── js/
│       └── app.js          # Client-side drag-and-drop, AJAX analysis, toasts
│
└── instance/
    └── notelens.db         # Auto-generated SQLite database file
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Git (optional)
- Tesseract OCR (Optional for live OCR, app handles missing binary gracefully)

### 2. Environment Setup

Using `uv` (recommended) or `venv`:

```bash
# Navigate to NoteLens directory
cd NoteLens

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows PowerShell:
.\.venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Tesseract OCR Installation (Windows)

1. Download the Tesseract Windows installer from UB-Mannheim or Tesseract GitHub repository.
2. Install to default path `C:\Program Files\Tesseract-OCR\tesseract.exe`.
3. If installed to a custom folder, navigate to **Settings** in the NoteLens application and save the custom path to `tesseract.exe`.

---

## 🏃 Run Application

```bash
# Run Flask app
python app.py
```

Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🧪 Testing NoteLens

1. **Dashboard & Demo Data**: Click **"Load Demo Notes"** on the Dashboard or Settings page to seed sample notes for Java, Operating Systems, DBMS, Networks, and Python.
2. **Uploading Notes**: Click **Upload Notes**, drag & drop an image, and click **Analyze Note**.
3. **Editing & Organization**: Modify extracted text, subject, or topic before saving. Note will instantly appear under the respective **Subject** and **Topic** catalogs.
4. **Search & Export**: Search keywords like `"deadlock"`, `"polymorphism"`, or `"sql"`, and export any note as TXT or PDF.

---

## 📜 License

MIT License • Created for College Student Productivity.
