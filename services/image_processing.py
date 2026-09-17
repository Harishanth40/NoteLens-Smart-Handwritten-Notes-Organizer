import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance

def preprocess_image(input_path, output_path):
    """
    Preprocess image for optimal OCR output.
    Steps: Grayscale -> Noise removal -> CLAHE contrast enhancement -> Deskew -> Adaptive threshold
    Returns output_path if successful, or input_path on error.
    """
    try:
        # Load image with OpenCV
        image = cv2.imread(input_path)
        if image is None:
            # Fallback PIL load
            pil_img = Image.open(input_path).convert('L')
            pil_img.save(output_path)
            return output_path

        # 1. Convert to Grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 2. Resize if too small/large for optimum OCR resolution
        height, width = gray.shape[:2]
        if max(height, width) < 1000:
            scale = 1000.0 / max(height, width)
            gray = cv2.resize(gray, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_CUBIC)
        elif max(height, width) > 3000:
            scale = 3000.0 / max(height, width)
            gray = cv2.resize(gray, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)

        # 3. Noise Removal (Bilateral filter to preserve sharp handwriting edges while smoothing noise)
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)

        # 4. Contrast Enhancement via CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        # 5. Deskewing
        deskewed = _deskew(enhanced)

        # 6. Adaptive Thresholding for crisp binarization
        thresh = cv2.adaptiveThreshold(
            deskewed, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31, 15
        )

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, thresh)
        return output_path

    except Exception as e:
        print(f"Error during image preprocessing: {e}")
        # Return input image path if preprocessing fails
        return input_path

def _deskew(image):
    """
    Calculates skew angle of handwritten text and rotates image.
    """
    try:
        # Invert image for contour detection
        inv = cv2.bitwise_not(image)
        coords = np.column_stack(np.where(inv > 0))
        if len(coords) < 10:
            return image
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # If angle is minor (e.g. less than 0.5 or greater than 20 deg), skip deskewing to prevent distortion
        if abs(angle) < 0.5 or abs(angle) > 25.0:
            return image

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated
    except Exception:
        return image
