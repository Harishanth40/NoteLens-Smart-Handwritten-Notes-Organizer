import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'notelens-secret-key-super-secure-2026'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Instance and Database settings
    INSTANCE_PATH = os.path.join(BASE_DIR, 'instance')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(INSTANCE_PATH, 'notelens.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    PROCESSED_FOLDER = os.path.join(UPLOAD_FOLDER, 'processed')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp', 'tiff'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    
    # Default Tesseract OCR path on Windows
    DEFAULT_TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
