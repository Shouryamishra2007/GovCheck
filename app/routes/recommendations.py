# ═══════════════════════════════════════════════════════════════
# FEATURE 9: Career Roadmap and Recommendations
# ═══════════════════════════════════════════════════════════════

from flask import Blueprint, request, jsonify
import logging
from app.services.recommendation_engine import CareerRoadmapGenerator
from app.services.ai_services import AICareerAssistant

logger = logging.getLogger(__name__)
recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/api/roadmaps', methods=['GET'])
def get_roadmaps():
    """Get all available career roadmaps."""
    try:
        generator = CareerRoadmapGenerator()
        roadmaps = generator.get_all_roadmaps()
        
        return jsonify({
            'success': True,
            'roadmaps': roadmaps
        })
    
    except Exception as e:
        logger.error(f"Roadmaps error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@recommendations_bp.route('/api/roadmap/<roadmap_key>', methods=['GET'])
def get_roadmap_detail(roadmap_key):
    """Get detailed roadmap for a specific path."""
    try:
        generator = CareerRoadmapGenerator()
        
        # Extract education and specialization from key
        # Format: '12th_engineering', 'graduation_tech', etc.
        parts = roadmap_key.split('_')
        education = parts[0] if len(parts) > 0 else '12th'
        specialization = parts[1] if len(parts) > 1 else None
        
        roadmap = generator.generate_roadmap(education, specialization)
        
        return jsonify(roadmap)
    
    except Exception as e:
        logger.error(f"Roadmap detail error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@recommendations_bp.route('/api/career-guidance', methods=['POST'])
def career_guidance():
    """FEATURE 4: Get personalized career guidance."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'success': False, 'error': 'Query required'}), 400
        
        # Import here to avoid circular imports
        from flask import current_app
        exam_service = current_app.config['EXAM_SERVICE']
        
        assistant = AICareerAssistant(exam_service)
        guidance = assistant.get_career_guidance(query)
        
        return jsonify(guidance)
    
    except Exception as e:
        logger.error(f"Career guidance error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400
