# ═══════════════════════════════════════════════════════════════
# FEATURES 3 & 4: Gemini AI Integration
# Purpose: Notification summarization & career guidance
# ═══════════════════════════════════════════════════════════════

import os
import logging
import json
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class AICareerAssistant:
    """
    FEATURE 4: Career guidance chatbot using GovCheck data.
    Recommends opportunities based on qualifications and goals.
    """

    def __init__(self, exam_service):
        self.exam_service = exam_service
        self.logger = logging.getLogger(__name__)

    def get_career_guidance(self, query: str, user_profile: Dict = None) -> Dict[str, Any]:
        """
        Provide personalized career guidance.
        
        Example queries:
        - "What opportunities are suitable for a Cybersecurity student?"
        - "What exams can I apply for after graduation?"
        - "What scholarships are available?"
        """
        try:
            # Get relevant exams from database
            all_exams = self.exam_service.exams
            relevant_exams = self._filter_relevant_exams(all_exams, query)
            
            if not relevant_exams:
                return {
                    'success': True,
                    'guidance': 'No specific opportunities match your query. Try browsing all exams or contact support.',
                    'relevant_opportunities': []
                }
            
            # Build guidance response
            guidance_text = self._generate_guidance_text(query, relevant_exams)
            
            return {
                'success': True,
                'guidance': guidance_text,
                'relevant_opportunities': [
                    {
                        'name': e.get('name'),
                        'conducting_type': e.get('conducting_type'),
                        'description': e.get('description', '')[:100]
                    }
                    for e in relevant_exams[:5]
                ]
            }

        except Exception as e:
            self.logger.error(f"Career guidance error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _filter_relevant_exams(self, exams: List[Dict], query: str) -> List[Dict]:
        """Filter exams relevant to the query."""
        query_lower = query.lower()
        keywords = {
            'cybersecurity': ['ssc', 'nda', 'ifs', 'defence', 'crpf'],
            'engineering': ['gate', 'ies', 'ifs', 'nda', 'ese'],
            'scholarship': ['jrf', 'dsir', 'barc', 'csir'],
            'graduation': ['upsc', 'ssc', 'psc'],
            'banking': ['ibps', 'sbi', 'rbi', 'banking'],
            'railway': ['railway', 'rrb', 'rrc'],
            'civil': ['ias', 'ips', 'upsc'],
            'defence': ['nda', 'cds', 'defence'],
        }
        
        matched_exams = []
        matched_set = set()
        
        for exam in exams:
            exam_name = exam.get('name', '').lower()
            exam_id = exam.get('name')  # Use name as unique identifier
            
            if exam_id in matched_set:
                continue
                
            for keyword, exam_types in keywords.items():
                if keyword in query_lower:
                    if any(e_type.lower() in exam_name for e_type in exam_types):
                        matched_exams.append(exam)
                        matched_set.add(exam_id)
                        break
        
        return matched_exams[:10]

    def _generate_guidance_text(self, query: str, exams: List[Dict]) -> str:
        """Generate personalized guidance text."""
        if not exams:
            return "No opportunities found for your query."
        
        exam_names = ", ".join([e.get('name', 'Unknown') for e in exams[:3]])
        
        guidance = f"Based on your interest in '{query}', "
        guidance += f"we recommend exploring: {exam_names}. "
        guidance += "Each offers unique career paths and opportunities. "
        guidance += "Use our match score feature to see which aligns best with your profile."
        
        return guidance
