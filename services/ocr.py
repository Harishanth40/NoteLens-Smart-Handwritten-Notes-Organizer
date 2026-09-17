import os
import shutil
import pytesseract
from PIL import Image

def get_tesseract_cmd(configured_path=None):
    """
    Resolves Tesseract executable path from configured path, environment, or system PATH.
    """
    if configured_path and os.path.exists(configured_path):
        return configured_path

    # Check common Windows paths
    common_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        os.path.expanduser(r'~\AppData\Local\Tesseract-OCR\tesseract.exe'),
        os.path.expanduser(r'~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe')
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path

    # Check PATH
    tesseract_in_path = shutil.which('tesseract')
    if tesseract_in_path:
        return tesseract_in_path

    return None

def is_tesseract_available(configured_path=None):
    """
    Checks if Tesseract OCR binary is installed and executable.
    """
    cmd = get_tesseract_cmd(configured_path)
    if not cmd:
        return False
    try:
        pytesseract.pytesseract.tesseract_cmd = cmd
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False

def extract_text_from_image(image_path, configured_tesseract_path=None):
    """
    Extracts text from image file using pytesseract.
    Returns dictionary with:
    - success (bool)
    - text (str)
    - error (str or None)
    - tesseract_installed (bool)
    - raw_confidence (float)
    """
    cmd = get_tesseract_cmd(configured_tesseract_path)
    if not cmd:
        return {
            'success': False,
            'text': '',
            'error': 'Tesseract OCR is not installed or configured. Please install Tesseract and configure its path in Settings.',
            'tesseract_installed': False,
            'confidence': 0.0
        }

    try:
        pytesseract.pytesseract.tesseract_cmd = cmd
        img = Image.open(image_path)

        # OCR Text Extraction with Page Segmentation Mode 3 (Fully automatic page segmentation)
        extracted_text = pytesseract.image_to_string(img, lang='eng', config='--psm 3')

        # Clean extracted text
        cleaned_lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
        cleaned_text = '\n'.join(cleaned_lines)

        # Calculate average confidence from OCR data
        ocr_confidence = 0.0
        try:
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            confs = [int(c) for c in data.get('conf', []) if c != '-1' and c != -1]
            if confs:
                ocr_confidence = round(sum(confs) / len(confs), 1)
        except Exception:
            ocr_confidence = 75.0 if cleaned_text else 0.0

        return {
            'success': True,
            'text': cleaned_text,
            'error': None,
            'tesseract_installed': True,
            'confidence': ocr_confidence
        }

    except Exception as e:
        return {
            'success': False,
            'text': '',
            'error': f'OCR Processing failed: {str(e)}',
            'tesseract_installed': True,
            'confidence': 0.0
        }
