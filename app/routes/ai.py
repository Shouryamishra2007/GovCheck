# ═══════════════════════════════════════════════════════════════
# FEATURES 3 & 4: Groq AI Integration
# Purpose: Notification summarization & career guidance
# ═══════════════════════════════════════════════════════════════

from flask import Blueprint, request, jsonify, current_app
import os
import re
import logging
import json

logger = logging.getLogger(__name__)
ai_bp = Blueprint('ai', __name__)

GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')


@ai_bp.route('/summarize', methods=['POST'])
def summarize():
    """FEATURE 3: Summarize government notification using Groq AI."""
    text = (request.json or {}).get('text', '').strip()
    if not text:
        return jsonify({'success': False, 'error': 'No notification text provided'}), 400
    if len(text) < 50:
        return jsonify({'success': False, 'error': 'Text too short to summarize'}), 400

    try:
        summary = _summarize_with_groq(text)
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        logger.error(f"AI summarize error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_bp.route('/career-guidance', methods=['POST'])
def career_guidance():
    """FEATURE 4: Get personalized career guidance using Groq AI."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'success': False, 'error': 'Query required'}), 400
        
        exam_service = current_app.config['EXAM_SERVICE']
        guidance = _get_career_guidance_with_groq(query, exam_service)
        
        return jsonify(guidance)
    
    except Exception as e:
        logger.error(f"Career guidance error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


def _summarize_with_groq(text: str) -> dict:
    """
    Summarize government notification using Groq AI (faster & cheaper than Gemini).
    """
    try:
        from groq import Groq
        
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set. Add it to your environment variables.")
        
        client = Groq(api_key=GROQ_API_KEY)
        
        prompt = f"""You are an expert at analyzing Indian government job/exam notifications.
Analyze the following notification and return ONLY a JSON object (no markdown fences) with these keys:
- eligibility: string (who can apply)
- age_limit: string (age range / relaxations)
- important_dates: object with keys like "application_start", "application_end", "exam_date" (string values)
- selection_process: list of strings (e.g., ["Written Exam", "Interview", "Medical Test"])
- required_documents: list of strings (e.g., ["10th Mark Sheet", "ID Proof"])
- quick_summary: string (2-3 sentences, plain language)

Notification text:
\"\"\"
{text[:3000]}
\"\"\"

Return valid JSON only:"""
        
        message = client.messages.create(
            model="mixtral-8x7b-32768",  # Fast & efficient Groq model
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Parse JSON from response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            result = json.loads(json_str)
            return result
        
        # Fallback: return structured response
        return {
            'quick_summary': response_text[:200],
            'eligibility': 'Unable to parse',
            'age_limit': 'Unable to parse',
            'important_dates': {},
            'selection_process': [],
            'required_documents': []
        }

    except ImportError:
        logger.error("Groq library not installed. Run: pip install groq")
        raise ValueError("Groq SDK not installed. Install with: pip install groq")
    except Exception as e:
        logger.error(f"Groq API error: {str(e)}")
        raise


def _get_career_guidance_with_groq(query: str, exam_service) -> dict:
    """
    Provide personalized career guidance using Groq AI.
    """
    try:
        from groq import Groq
        
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set. Add it to your environment variables.")
        
        # Get relevant exams from database
        all_exams = exam_service.exams
        relevant_exams = _filter_relevant_exams(all_exams, query)
        
        if not relevant_exams:
            return {
                'success': True,
                'guidance': 'No specific opportunities match your query. Try browsing all exams or contact support.',
                'relevant_opportunities': []
            }
        
        # Build context with top exams
        exam_context = "\n".join([
            f"- {e.get('name')}: {e.get('conducting_type')} ({e.get('govt_type', 'Government')})"
            for e in relevant_exams[:5]
        ])
        
        client = Groq(api_key=GROQ_API_KEY)
        
        prompt = f"""You are India's leading career counselor specializing in government jobs and education.
A student asks: "{query}"

Here are relevant opportunities from our database:
{exam_context}

Provide:
1. A personalized response addressing their query (2-3 sentences)
2. List 3-5 specific opportunities they should explore
3. Action steps they should take next
4. Timeline/roadmap if applicable

Be encouraging and practical. Focus on their strengths."""
        
        message = client.messages.create(
            model="mixtral-8x7b-32768",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        guidance_text = message.content[0].text
        
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

    except ImportError:
        logger.error("Groq library not installed. Run: pip install groq")
        raise ValueError("Groq SDK not installed. Install with: pip install groq")
    except Exception as e:
        logger.error(f"Groq API error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def _filter_relevant_exams(exams, query: str):
    """Filter exams relevant to the query."""
    query_lower = query.lower()
    keywords = {
        'cybersecurity': ['ssc', 'nda', 'ifs', 'defence', 'crpf', 'ib'],
        'engineering': ['gate', 'ies', 'ifs', 'nda', 'ese', 'isro', 'drdo'],
        'scholarship': ['jrf', 'dsir', 'barc', 'csir'],
        'graduation': ['upsc', 'ssc', 'psc'],
        'banking': ['ibps', 'sbi', 'rbi', 'banking'],
        'railway': ['railway', 'rrb', 'rrc'],
        'civil': ['ias', 'ips', 'upsc'],
        'defence': ['nda', 'cds', 'defence', 'army'],
    }
    
    matched_exams = []
    matched_set = set()
    
    for exam in exams:
        exam_name = exam.get('name', '').lower()
        exam_id = exam.get('name')
        
        if exam_id in matched_set:
            continue
            
        for keyword, exam_types in keywords.items():
            if keyword in query_lower:
                if any(e_type.lower() in exam_name for e_type in exam_types):
                    matched_exams.append(exam)
                    matched_set.add(exam_id)
                    break
    
    return matched_exams[:10]
