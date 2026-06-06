from flask import Blueprint, request, jsonify, current_app
import logging

exams_bp = Blueprint('exams', __name__)
logger = logging.getLogger(__name__)


def get_service():
    return current_app.config['EXAM_SERVICE']


@exams_bp.route('/get-exams', methods=['POST'])
def get_exams():
    svc = get_service()
    valid, user, err = svc.validate(request.form)
    if not valid:
        return jsonify({'success': False, 'error': err}), 400

    results = svc.filter(user)
    central, state = svc.separate(results)

    return jsonify({
        'success': True,
        'results': results,
        'central_exams': central,
        'state_exams': state,
        'total_count': len(results),
        'central_count': len(central),
        'state_count': len(state)
    })


@exams_bp.route('/search', methods=['GET'])
def search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'success': False, 'error': 'Query required'}), 400
    svc = get_service()
    results = svc.search(q)
    return jsonify({'success': True, 'results': results, 'count': len(results)})
