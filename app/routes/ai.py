from flask import Blueprint, request, jsonify
import os, re, logging

ai_bp = Blueprint('ai', __name__)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')


@ai_bp.route('/summarize', methods=['POST'])
def summarize():
    text = (request.json or {}).get('text', '').strip()
    if not text:
        return jsonify({'success': False, 'error': 'No notification text provided'}), 400
    if len(text) < 50:
        return jsonify({'success': False, 'error': 'Text too short to summarize'}), 400

    try:
        summary = _summarize_with_gemini(text)
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        logger.error(f"AI summarize error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def _summarize_with_gemini(text: str) -> dict:
    import urllib.request, json as _json

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set. Add it to your environment variables.")

    prompt = f"""You are an expert at analysing Indian government job/exam notifications.
Analyse the following notification and return ONLY a JSON object (no markdown fences) with these keys:
- eligibility: string (who can apply)
- age_limit: string (age range / relaxations)
- important_dates: object with keys like "application_start", "application_end", "exam_date" (string values)
- selection_process: list of strings
- required_documents: list of strings
- quick_summary: string (2-3 sentences, plain language)

Notification text:
\"\"\"
{text[:4000]}
\"\"\"
"""

    payload = _json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode()

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    req = urllib.request.Request(url, data=payload,
                                 headers={'Content-Type': 'application/json'}, method='POST')

    with urllib.request.urlopen(req, timeout=20) as resp:
        data = _json.loads(resp.read())

    raw = data['candidates'][0]['content']['parts'][0]['text']
    # Strip markdown fences if present
    raw = re.sub(r'^```[a-z]*\n?', '', raw.strip())
    raw = re.sub(r'\n?```$', '', raw.strip())
    return _json.loads(raw)
