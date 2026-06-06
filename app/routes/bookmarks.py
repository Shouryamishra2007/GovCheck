# ═══════════════════════════════════════════════════════════════
# FEATURE 7: Bookmark System (Local Storage + Database Ready)
# ═══════════════════════════════════════════════════════════════

from flask import Blueprint, request, jsonify
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)
bookmarks_bp = Blueprint('bookmarks', __name__)


@bookmarks_bp.route('/api/bookmarks/add', methods=['POST'])
def add_bookmark():
    """Save an exam to bookmarks."""
    try:
        data = request.get_json()
        exam_id = data.get('exam_id')
        exam_name = data.get('exam_name')
        
        if not exam_id:
            return jsonify({'success': False, 'error': 'exam_id required'}), 400
        
        # In production: save to database
        # For now: return success for client-side LocalStorage handling
        
        return jsonify({
            'success': True,
            'message': f'Bookmarked: {exam_name}',
            'exam_id': exam_id,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Bookmark error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@bookmarks_bp.route('/api/bookmarks/remove', methods=['POST'])
def remove_bookmark():
    """Remove exam from bookmarks."""
    try:
        data = request.get_json()
        exam_id = data.get('exam_id')
        
        if not exam_id:
            return jsonify({'success': False, 'error': 'exam_id required'}), 400
        
        return jsonify({'success': True, 'exam_id': exam_id})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@bookmarks_bp.route('/api/bookmarks/list', methods=['GET'])
def list_bookmarks():
    """Get all bookmarked exams (stub for frontend to query)."""
    return jsonify({'bookmarks': []})