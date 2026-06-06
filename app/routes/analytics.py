from flask import Blueprint, jsonify, current_app

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/analytics')
def analytics():
    svc = current_app.config['EXAM_SERVICE']
    return jsonify({'success': True, 'data': svc.analytics()})
