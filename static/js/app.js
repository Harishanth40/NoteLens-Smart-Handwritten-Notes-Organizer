/* NoteLens Client Interactivity & AJAX Engine */

document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initUploadDropzone();
});

/* Theme Switcher (Dark / Light) */
function initThemeToggle() {
    const themeBtn = document.getElementById('themeToggleBtn');
    if (!themeBtn) return;

    // Load saved theme or default to light
    const savedTheme = localStorage.getItem('notelens_theme') || 'light';
    setTheme(savedTheme);

    themeBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('notelens_theme', theme);
    
    const icon = document.getElementById('themeIcon');
    if (icon) {
        if (theme === 'dark') {
            icon.className = 'bi bi-sun-fill text-warning';
        } else {
            icon.className = 'bi bi-moon-stars-fill text-dark';
        }
    }
}

/* Toast Notifications Engine */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toastId = 'toast_' + Date.now();
    const bgClass = type === 'danger' ? 'bg-danger text-white' :
                    type === 'success' ? 'bg-success text-white' :
                    type === 'warning' ? 'bg-warning text-dark' : 'bg-primary text-white';

    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 shadow-lg" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body font-weight-bold">
                    ${message}
                </div>
                <button type="button" class="btn-close ${type !== 'warning' ? 'btn-close-white' : ''} me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', toastHtml);
    const toastElem = document.getElementById(toastId);
    const bsToast = new bootstrap.Toast(toastElem, { delay: 4500 });
    bsToast.show();

    toastElem.addEventListener('hidden.bs.toast', () => {
        toastElem.remove();
    });
}

/* Upload Page Drag & Drop and AJAX Analysis */
let selectedFile = null;

function initUploadDropzone() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('imageFileInput');
    const analyzeBtn = document.getElementById('analyzeBtn');

    if (!dropzone || !fileInput) return;

    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleSelectedFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleSelectedFile(e.target.files[0]);
        }
    });

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', runImageAnalysis);
    }
}

function handleSelectedFile(file) {
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/bmp'];
    if (!validTypes.includes(file.type)) {
        showToast('Invalid file format. Please upload PNG, JPG, JPEG, or WEBP image.', 'danger');
        return;
    }

    if (file.size > 16 * 1024 * 1024) {
        showToast('File size exceeds maximum 16MB limit.', 'danger');
        return;
    }

    selectedFile = file;

    // Show image preview
    const reader = new FileReader();
    reader.onload = (e) => {
        const previewImg = document.getElementById('previewImage');
        const previewBox = document.getElementById('previewSection');
        if (previewImg && previewBox) {
            previewImg.src = e.target.result;
            previewBox.classList.remove('d-none');
        }
    };
    reader.readAsDataURL(file);

    showToast('File selected: ' + file.name, 'info');
}

function runImageAnalysis() {
    if (!selectedFile) {
        showToast('Please select or drop an image file first.', 'warning');
        return;
    }

    const loadingSpinner = document.getElementById('loadingSection');
    const resultsSection = document.getElementById('resultsSection');
    const analyzeBtn = document.getElementById('analyzeBtn');

    if (loadingSpinner) loadingSpinner.classList.remove('d-none');
    if (resultsSection) resultsSection.classList.add('d-none');
    if (analyzeBtn) analyzeBtn.disabled = true;

    const formData = new FormData();
    formData.append('image', selectedFile);

    fetch('/api/analyze', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (loadingSpinner) loadingSpinner.classList.add('d-none');
        if (analyzeBtn) analyzeBtn.disabled = false;

        if (!data.success) {
            showToast(data.error || 'Failed to process note image.', 'danger');
            return;
        }

        showToast('Image analysis complete!', 'success');

        if (data.ocr_warning) {
            showToast(data.ocr_warning, 'warning');
        }

        // Fill form fields
        document.getElementById('formTitle').value = data.suggested_title || 'Untitled Note';
        document.getElementById('formExtractedText').value = data.extracted_text || '';
        document.getElementById('formSubject').value = data.subject || 'Other';
        document.getElementById('formTopic').value = data.topic || 'General';
        document.getElementById('formConfidence').value = data.confidence || 0.0;
        document.getElementById('formImageFilename').value = data.image_filename;
        document.getElementById('formProcessedFilename').value = data.processed_filename;
        document.getElementById('formOriginalFilename').value = data.original_filename;

        // Update confidence badge
        const confBadge = document.getElementById('displayConfidenceBadge');
        if (confBadge) {
            confBadge.textContent = `${data.confidence}% Confidence`;
            if (data.confidence > 80) confBadge.className = 'badge bg-success fs-6';
            else if (data.confidence > 50) confBadge.className = 'badge bg-primary fs-6';
            else confBadge.className = 'badge bg-warning text-dark fs-6';
        }

        if (resultsSection) resultsSection.classList.remove('d-none');

        // Check for duplicates
        if (data.is_duplicate) {
            showToast(`Duplicate alert: Note matches existing note "${data.similar_note.title}" (${data.similarity_score}% similarity)`, 'warning');
            const dupAlert = document.getElementById('duplicateAlertBox');
            if (dupAlert) {
                document.getElementById('dupTitle').textContent = data.similar_note.title;
                document.getElementById('dupScore').textContent = data.similarity_score;
                document.getElementById('dupViewLink').href = `/notes/${data.similar_note.id}`;
                dupAlert.classList.remove('d-none');
            }
        }

    })
    .catch(err => {
        if (loadingSpinner) loadingSpinner.classList.add('d-none');
        if (analyzeBtn) analyzeBtn.disabled = false;
        showToast('Network error analyzing note: ' + err.message, 'danger');
    });
}
