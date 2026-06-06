# Enhanced exams route with smart search

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
        exams = exam_service.filter_exams(age, status, category, state)

        if not exams:
            return jsonify({'success': False, 'error': 'No matching exams found'})

        # Score each exam
        from app.services.scoring_engine import OpportunityScorer
        scorer = OpportunityScorer()
        user_profile = {
            'age': age,
            'education': status,
            'category': category,
            'state': state
        }

        scored_exams = scorer.rank_exams(exams, user_profile)
        
        return jsonify({
            'success': True,
            'results': scored_exams,
            'count': len(scored_exams)
        })

    except Exception as e:
        logger.error(f"Error in get_exams: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@exams_bp.route('/search', methods=['GET'])
def smart_search():
    """FEATURE 2: Intelligent search with fuzzy matching."""
    try:
        query = request.args.get('q', '').lower().strip()
        
        if len(query) < 2:
            return jsonify({'results': []})

        exam_service = current_app.config['EXAM_SERVICE']
        all_exams = exam_service.get_all_exams()
        
        # Multi-field search with scoring
        results = []
        
        for exam in all_exams:
            score = 0
            name = exam.get('name', '').lower()
            conducting = exam.get('conducting_type', '').lower()
            description = exam.get('description', '').lower()
            
            # Exact match boost
            if query in name:
                score += 100
            elif query in conducting:
                score += 80
            elif query in description:
                score += 50
            
            # Fuzzy matching for typos
            name_ratio = SequenceMatcher(None, query, name).ratio()
            if name_ratio > 0.7:
                score += int(name_ratio * 100)
            
            if score > 0:
                results.append((exam, score))
        
        # Sort by score and return top 10
        results.sort(key=lambda x: x[1], reverse=True)
        return jsonify({
            'results': [r[0] for r in results[:10]],
            'count': len(results)
        })

    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'results': []}), 400