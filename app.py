import os
from flask import Flask, send_from_directory, render_template
from config import Config
from database import db
from database.models import Note, SystemSetting
from routes.main import main_bp
from routes.notes import notes_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure required directories exist
    os.makedirs(app.config['INSTANCE_PATH'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(notes_bp)

    # Serve uploaded images route
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Custom Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return render_template('500.html', message="File size exceeds maximum upload limit of 16MB."), 413

    # Initialize Database tables inside context
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    print("Starting NoteLens Web Application on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
