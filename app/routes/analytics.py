# ═══════════════════════════════════════════════════════════════
# FEATURE 8: Analytics Dashboard
# ═══════════════════════════════════════════════════════════════

from flask import Blueprint, jsonify, current_app
from collections import Counter
import logging

logger = logging.getLogger(__name__)
analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/api/analytics/dashboard', methods=['GET'])
def get_analytics_dashboard():
    """
    Return comprehensive analytics:
    - Total opportunities
    - Central vs State split
    - Top opportunities
    - Upcoming deadlines
    - State-wise distribution
    """
    try:
        exam_service = current_app.config['EXAM_SERVICE']
        exams = exam_service.get_all_exams()
        
        if not exams:
            return jsonify({'success': False}), 400
        
        # Calculate metrics
        total = len(exams)
        central = len([e for e in exams 
                       if 'CENTRAL' in (e.get('govt_type', '').upper())])
        state = total - central
        
        # Top opportunities by interest
        all_names = [e.get('name', '') for e in exams]
        top_exams = Counter(all_names).most_common(5)
        
        # State distribution
        state_dist = {}
        for exam in exams:
            states = exam.get('states', [])
            if isinstance(states, list):
                for s in states:
                    state_dist[s] = state_dist.get(s, 0) + 1
        
        # Group by conducting body
        body_dist = {}
        for exam in exams:
            body = exam.get('conducting_type', 'Other')
            body_dist[body] = body_dist.get(body, 0) + 1
        
        return jsonify({
            'success': True,
            'metrics': {
                'total_opportunities': total,
                'central_opportunities': central,
                'state_opportunities': state,
            },
            'top_opportunities': [
                {'name': name, 'count': count} 
                for name, count in top_exams
            ],
            'state_distribution': state_dist,
            'body_distribution': body_dist
        })

    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@analytics_bp.route('/api/analytics/education', methods=['GET'])
def education_analytics():
    """FEATURE 11: Education-wise eligibility analysis."""
    try:
        exam_service = current_app.config['EXAM_SERVICE']
        exams = exam_service.get_all_exams()
        
        education_reqs = {}
        for exam in exams:
            edu = exam.get('education_required', 'Unknown')
            if edu not in education_reqs:
                education_reqs[edu] = []
            education_reqs[edu].append(exam['name'])
        
        return jsonify({
            'success': True,
            'education_distribution': {
                k: len(v) for k, v in education_reqs.items()
            },
            'details': education_reqs
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400