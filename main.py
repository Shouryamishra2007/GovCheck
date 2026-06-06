import logging
import os
from flask import Flask
from flask_cors import CORS

from app.routes.exams import exams_bp
from app.routes.ai import ai_bp
from app.routes.analytics import analytics_bp
from app.services.exam_services import ExamService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('govcheck.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    CORS(app)

    # Load exam data once at startup
    exam_service = ExamService()
    app.config['EXAM_SERVICE'] = exam_service
    logger.info(f"GovCheck started — {exam_service.total_count} exams loaded")

    app.register_blueprint(exams_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(analytics_bp)

    from flask import render_template, jsonify

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'exams_loaded': exam_service.total_count
        })

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Server error'}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
