from difflib import SequenceMatcher
import re

def clean_text_for_comparison(text):
    """
    Normalizes text for duplicate comparison.
    """
    if not text:
        return ''
    # Lowercase, remove non-alphanumeric chars, compress whitespace
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
    return ' '.join(cleaned.split())

def calculate_similarity(text1, text2):
    """
    Calculates combined sequence ratio and word Jaccard similarity.
    Returns float percentage (0.0 to 100.0).
    """
    norm1 = clean_text_for_comparison(text1)
    norm2 = clean_text_for_comparison(text2)

    if not norm1 or not norm2:
        return 0.0

    if norm1 == norm2:
        return 100.0

    # 1. SequenceMatcher ratio
    seq_ratio = SequenceMatcher(None, norm1, norm2).ratio()

    # 2. Word set Jaccard similarity
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    if not words1 or not words2:
        jaccard = 0.0
    else:
        jaccard = len(words1.intersection(words2)) / len(words1.union(words2))

    # Weighted average: 60% sequence ratio + 40% Jaccard index
    combined_score = (seq_ratio * 0.60) + (jaccard * 0.40)
    return round(combined_score * 100.0, 1)

def find_duplicate_note(extracted_text, existing_notes, threshold=70.0):
    """
    Checks extracted_text against a list of Note objects.
    Returns dict with duplicate status, matching note details, and score.
    """
    if not extracted_text or not existing_notes:
        return {'is_duplicate': False, 'similar_note': None, 'similarity_score': 0.0}

    highest_score = 0.0
    most_similar_note = None

    for note in existing_notes:
        score = calculate_similarity(extracted_text, note.extracted_text)
        if score > highest_score:
            highest_score = score
            most_similar_note = note

    if highest_score >= threshold and most_similar_note:
        return {
            'is_duplicate': True,
            'similar_note': most_similar_note.to_dict(),
            'similarity_score': highest_score
        }

    return {
        'is_duplicate': False,
        'similar_note': None,
        'similarity_score': highest_score
    }
