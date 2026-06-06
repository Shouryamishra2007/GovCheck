# ═══════════════════════════════════════════════════════════════
# FEATURES 3 & 4: Gemini AI Integration
# Purpose: Notification summarization & career guidance
# ═══════════════════════════════════════════════════════════════

import os
import logging
import json
from typing import Dict, Any, List
import google.genai as genai

logger = logging.getLogger(__name__)


class AINotificationSummarizer:
    """
    FEATURE 3: Parse government notification text and extract:
    - Eligibility criteria
    - Age limits
    - Important dates
    - Selection process
    - Documents required
    """

    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.logger = logging.getLogger(__name__)

    def summarize_notification(self, notification_text: str) -> Dict[str, Any]:
        """
        Summarize government notification using Gemini AI.
        
        Returns:
            {
                'quick_summary': str,
                'eligibility': str,
                'age_limit': str,
                'important_dates': {key: date},
                'selection_process': [steps],
                'required_documents': [docs],
                'success': bool
            }
        """
        try:
            prompt = f"""
You are an expert in parsing Indian government job notifications.
Extract and structure the following from this notification:

1. Eligibility criteria (brief)
2. Age limits (with relaxation for categories if applicable)
3. Important dates (Application deadline, exam date, etc.) - return as key-value pairs
4. Selection process steps (written exam, interview, etc.)
5. Required documents (10th mark sheet, ID proof, etc.)
6. A quick 2-3 sentence summary

Notification Text:
{notification_text[:3000]}  # Limit to 3000 chars to save tokens

Return ONLY a JSON object with keys:
- quick_summary: str
- eligibility: str
- age_limit: str
- important_dates: {{}}
- selection_process: []
- required_documents: []

Make sure JSON is valid.
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Parse JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)
                result['success'] = True
                return result
            
            return {
                'success': False,
                'error': 'Could not parse AI response'
            }

        except Exception as e:
            self.logger.error(f"Summarization error: {str(e)}")
            return {
                'success': False,
                'error': f'AI Error: {str(e)}'
            }


class AICareerAssistant:
    """
    FEATURE 4: Career guidance chatbot using GovCheck data.
    Recommends opportunities based on qualifications and goals.
    """

    def __init__(self, exam_service):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
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
            all_exams = self.exam_service.get_all_exams()
            relevant_exams = self._filter_relevant_exams(all_exams, query)
            
            exams_context = json.dumps(relevant_exams[:5], indent=2)  # Top 5 exams
            
            prompt = f"""
You are India's leading career counselor specializing in government jobs and education.
A student asks: "{query}"

Here are relevant opportunities from our database:
{exams_context}

Provide:
1. A personalized response addressing their query (2-3 sentences)
2. List 3-5 specific opportunities they should explore
3. Action steps they should take next
4. Timeline/roadmap if applicable

Be encouraging and practical. Focus on their strengths.
"""
            
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'guidance': response.text,
                'relevant_opportunities': [e['name'] for e in relevant_exams[:5]]
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
            'cybersecurity': ['ssc', 'nda', 'ifs', 'defence'],
            'engineering': ['gate', 'ies', 'ifs', 'nda'],
            'scholarship': ['jrf', 'dsir', 'barc'],
            'graduation': ['upsc', 'ssc', 'psc'],
            'banking': ['ibps', 'sbi', 'rbi'],
            'railway': ['railway', 'rrb'],
        }
        
        matched_exams = []
        for exam in exams:
            exam_name = exam.get('name', '').lower()
            for keyword, exam_types in keywords.items():
                if keyword in query_lower:
                    if any(e_type in exam_name for e_type in exam_types):
                        matched_exams.append(exam)
                        break
        
        return matched_exams[:10]