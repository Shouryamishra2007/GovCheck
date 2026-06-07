from flask import Blueprint, request, jsonify, current_app
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)
exams_bp = Blueprint('exams', __name__)


@exams_bp.route('/get-exams', methods=['POST'])
def get_exams():
    """Get filtered exams with match scores."""
    try:
        age = int(request.form.get('age', 18))
        status = request.form.get('status', 'graduation')
        category = request.form.get('category', 'general')
        state = request.form.get('state', 'delhi')

        exam_service = current_app.config['EXAM_SERVICE']
        
        # Validate user input
        valid, user_data, error = exam_service.validate({
            'age': age,
            'status': status,
            'category': category,
            'state': state
        })
        
        if not valid:
            return jsonify({'success': False, 'error': error}), 400

        # Filter exams using existing filter method
        exams = exam_service.filter(user_data)

        if not exams:
            return jsonify({'success': False, 'error': 'No matching exams found'})

        return jsonify({
            'success': True,
            'results': exams,
            'count': len(exams)
        })

    except Exception as e:
        logger.error(f"Error in get_exams: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@exams_bp.route('/search', methods=['GET'])
def smart_search():
    """FEATURE 2: Intelligent search with fuzzy matching."""
    try:
        query = request.args.get('q', '').lower().strip()
        
        if len(query) < 1:
            return jsonify({'results': []})

        exam_service = current_app.config['EXAM_SERVICE']
        results = exam_service.search(query)
        
        return jsonify({
            'results': results,
            'count': len(results)
        })

    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'results': []}), 400
