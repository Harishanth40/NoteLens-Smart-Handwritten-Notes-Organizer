import sys
import os

# Add NoteLens directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_subject_detection():
    from services.subject_detector import detect_subject

    # Test case 1: Operating Systems
    text_os = "Deadlock occurs when two or more processes wait indefinitely for resources held by each other..."
    subject, conf = detect_subject(text_os)
    print(f"[TEST] OS Detection Result: subject='{subject}', confidence={conf}%")
    assert subject == 'Operating Systems', f"Expected 'Operating Systems', got '{subject}'"

    # Test case 2: Java
    text_java = "class, object, inheritance, polymorphism, encapsulation, interface, exception handling"
    subject, conf = detect_subject(text_java)
    print(f"[TEST] Java Detection Result: subject='{subject}', confidence={conf}%")
    assert subject == 'Java', f"Expected 'Java', got '{subject}'"

    # Test case 3: DBMS
    text_dbms = "database, SQL, normalization, 1NF, 2NF, 3NF, BCNF, primary key, foreign key, transaction"
    subject, conf = detect_subject(text_dbms)
    print(f"[TEST] DBMS Detection Result: subject='{subject}', confidence={conf}%")
    assert subject == 'DBMS', f"Expected 'DBMS', got '{subject}'"

    print("[OK] Subject Detection tests passed successfully!")

def test_topic_detection():
    from services.topic_detector import detect_topic

    # Test case 1: Deadlock under Operating Systems
    text_os = "Deadlock occurs when two processes wait for resources held by each other. Banker algorithm avoids deadlock."
    topic = detect_topic(text_os, 'Operating Systems')
    print(f"[TEST] Topic Detection Result for OS: '{topic}'")
    assert topic == 'Deadlock', f"Expected 'Deadlock', got '{topic}'"

    # Test case 2: Normalization under DBMS
    text_db = "1NF 2NF 3NF BCNF functional dependency decomposition"
    topic = detect_topic(text_db, 'DBMS')
    print(f"[TEST] Topic Detection Result for DBMS: '{topic}'")
    assert topic == 'Normalization', f"Expected 'Normalization', got '{topic}'"

    print("[OK] Topic Detection tests passed successfully!")

def test_similarity():
    from services.similarity import calculate_similarity

    t1 = "Deadlock occurs when two or more processes wait indefinitely for resources held by each other."
    t2 = "Deadlock occurs when processes wait indefinitely for resources held by each other."
    score = calculate_similarity(t1, t2)
    print(f"[TEST] Text Similarity score: {score}%")
    assert score >= 70.0, f"Expected similarity score >= 70%, got {score}%"

    print("[OK] Similarity calculation tests passed successfully!")

def test_flask_app():
    from app import app
    from database import db
    from database.models import Note

    with app.app_context():
        # Create tables
        db.create_all()
        
        # Count notes
        count = Note.query.count()
        print(f"[TEST] Flask app database connected. Total notes in DB: {count}")
        
        # Test client
        client = app.test_client()

        # Test GET /
        res = client.get('/')
        assert res.status_code == 200, f"Expected 200 from /, got {res.status_code}"
        print("[OK] Landing page GET / returned 200 OK")

        # Test GET /dashboard
        res = client.get('/dashboard')
        assert res.status_code == 200, f"Expected 200 from /dashboard, got {res.status_code}"
        print("[OK] Dashboard GET /dashboard returned 200 OK")

        # Test POST /demo/load
        res = client.post('/demo/load', follow_redirects=True)
        assert res.status_code == 200, f"Expected 200 after loading demo data, got {res.status_code}"
        
        demo_count = Note.query.count()
        print(f"[TEST] Demo data loaded! Total notes in DB now: {demo_count}")
        assert demo_count >= 5, f"Expected at least 5 demo notes, got {demo_count}"

        # Test GET /notes
        res = client.get('/notes')
        assert res.status_code == 200, f"Expected 200 from /notes, got {res.status_code}"
        print("[OK] Notes list GET /notes returned 200 OK")

        # Test GET /subjects
        res = client.get('/subjects')
        assert res.status_code == 200, f"Expected 200 from /subjects, got {res.status_code}"
        print("[OK] Subjects list GET /subjects returned 200 OK")

        # Test GET /search?q=deadlock
        res = client.get('/search?q=deadlock')
        assert res.status_code == 200, f"Expected 200 from /search, got {res.status_code}"
        assert b'Deadlock' in res.data, "Expected 'Deadlock' search result"
        print("[OK] Search GET /search?q=deadlock returned matching note")

        # Test PDF export for note 1
        note1 = Note.query.first()
        res = client.get(f'/notes/{note1.id}/download/pdf')
        assert res.status_code == 200, f"Expected 200 for PDF download, got {res.status_code}"
        assert res.mimetype == 'application/pdf', f"Expected pdf mimetype, got {res.mimetype}"
        print(f"[OK] PDF Download for Note #{note1.id} generated valid PDF byte stream")

        # Test TXT export for note 1
        res = client.get(f'/notes/{note1.id}/download/txt')
        assert res.status_code == 200, f"Expected 200 for TXT download, got {res.status_code}"
        assert b'NOTELENS' in res.data, "Expected NOTELENS header in TXT output"
        print(f"[OK] TXT Download for Note #{note1.id} generated valid TXT file")

if __name__ == '__main__':
    print("--- STARTING NOTELENS SUITE TESTS ---")
    test_subject_detection()
    test_topic_detection()
    test_similarity()
    test_flask_app()
    print("=== ALL NOTELENS SUITE TESTS PASSED SUCCESSFULLY! ===")
