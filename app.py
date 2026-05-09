import json
import logging
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('govcheck.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

EXAMS_DATA = []

def load_exams_data():
    try:
        # BUG FIX 1: was 'data/exams.json' but file lives at same level as app.py
        data_path = os.path.join(os.path.dirname(__file__), 'exams.json')
        if not os.path.exists(data_path):
            logger.warning(f"Exams data file not found at {data_path}")
            return []
        with open(data_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        logger.info(f"Successfully loaded {len(data)} exams from {data_path}")
        return data
    except Exception as e:
        logger.error(f"Error loading exams data: {str(e)}")
        return []

def validate_form_data(data):
    try:
        age_str = str(data.get('age', '')).strip()
        if not age_str:
            return False, None, "Age is required"
        try:
            age = int(age_str)
            if age < 10 or age > 60:
                return False, None, "Age must be between 10 and 60"
        except ValueError:
            return False, None, "Age must be a valid number"

        status = data.get('status', '').strip().lower()
        if not status:
            return False, None, "Education status is required"

        # BUG FIX 2: added '10th', 'graduation', 'post-graduation' to valid statuses
        valid_statuses = ['10th', '12th', '12', 'graduate', 'graduation', 'postgraduate', 'post-graduate', 'post-graduation', 'pg']
        if status not in valid_statuses:
            return False, None, f"Invalid education status. Got: {status}"

        # Normalize: map UI values to JSON eligibility values
        if status in ('post-graduate', 'postgraduate', 'pg'):
            status = 'post-graduation'
        elif status in ('graduate', 'graduation'):
            status = 'graduation'
        elif status == '12':
            status = '12th'

        category = data.get('category', '').strip().lower()
        if not category:
            return False, None, "Category is required"
        if category not in ['general', 'obc', 'sc', 'st']:
            return False, None, f"Invalid category. Got: {category}"

        state = data.get('state', '').strip().lower()
        if not state:
            return False, None, "State is required"

        cleaned_data = {'age': age, 'status': status, 'category': category, 'state': state}
        logger.info(f"Form data validated: {cleaned_data}")
        return True, cleaned_data, None
    except Exception as e:
        logger.error(f"Error validating form data: {str(e)}")
        return False, None, "Error validating form data"

def check_age_eligibility(user_age, user_category, exam):
    """
    BUG FIX 3: max_age is a dict {General, OBC, SC, ST} not a number.
    Must look up the right key for the user's category.
    """
    min_age = exam.get('min_age', 0)
    max_age_data = exam.get('max_age', 120)

    if isinstance(max_age_data, dict):
        cat_map = {'general': 'General', 'obc': 'OBC', 'sc': 'SC', 'st': 'ST'}
        cat_key = cat_map.get(user_category.lower(), 'General')
        max_age = max_age_data.get(cat_key, max_age_data.get('General', 120))
    else:
        max_age = int(max_age_data)

    return min_age <= user_age <= max_age

def check_education_eligibility(user_status, exam):
    """
    BUG FIX 4: JSON uses 'eligibility' not 'required_education'.
    """
    required_education = exam.get('eligibility', [])
    if not required_education or 'all' in required_education:
        return True

    # Normalize JSON eligibility values for comparison
    edu_order = {'10th': 1, '12th': 2, 'graduation': 3, 'post-graduation': 4}
    user_level = edu_order.get(user_status, 0)

    for edu in required_education:
        req_level = edu_order.get(edu.lower().strip(), 0)
        if user_level >= req_level and req_level > 0:
            return True

    return False

def check_state_eligibility(user_state, exam):
    """
    BUG FIX 5: 'type' field doesn't exist; use 'govt_type'.
    BUG FIX 6: exam_states can be a string 'all' — iterating over it gives
               individual characters, breaking the 'all in list' check.
    """
    # National selection matches everything
    if user_state in ('all', 'national', ''):
        return True

    # Central / Union Territory exams are pan-India
    govt_type = exam.get('govt_type', '').upper()
    if 'CENTRAL' in govt_type or 'UNION TERRITORY' in govt_type:
        return True

    exam_states = exam.get('states', [])

    def normalize(s):
        return s.lower().strip().replace('_', ' ')

    if isinstance(exam_states, str):
        if normalize(exam_states) == 'all':
            return True
        return normalize(user_state) == normalize(exam_states)

    if isinstance(exam_states, list):
        normalized = [normalize(s) for s in exam_states]
        if 'all' in normalized:
            return True
        return normalize(user_state) in normalized

    return True

def filter_exams(user_data, exams):
    filtered = []
    logger.info(f"Filtering {len(exams)} exams for user: {user_data}")

    for exam in exams:
        try:
            # BUG FIX 7: pass category to age check
            if not check_age_eligibility(user_data['age'], user_data['category'], exam):
                continue
            if not check_education_eligibility(user_data['status'], exam):
                continue
            # BUG FIX 8: removed separate category check (JSON has no eligible_categories;
            # all exams are open to all categories — age relaxation handles the difference)
            if not check_state_eligibility(user_data['state'], exam):
                continue
            filtered.append(exam)
        except Exception as e:
            logger.warning(f"Error checking exam {exam.get('name')}: {e}")
            continue

    logger.info(f"Matched {len(filtered)} exams")
    return filtered

def separate_exams_by_type(exams):
    """BUG FIX 9: was using 'type' field; JSON has 'govt_type'."""
    central, state = [], []
    for exam in exams:
        govt_type = exam.get('govt_type', '').upper()
        if 'CENTRAL' in govt_type or 'UNION TERRITORY' in govt_type:
            central.append(exam)
        else:
            state.append(exam)
    return central, state

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return jsonify({'error': 'Error loading page'}), 500

@app.route('/get-exams', methods=['POST'])
def get_exams():
    try:
        logger.info("POST /get-exams")
        is_valid, cleaned_data, error_message = validate_form_data(request.form)

        if not is_valid:
            return jsonify({'success': False, 'error': error_message, 'results': []}), 400

        if not EXAMS_DATA:
            return jsonify({'success': False, 'error': 'Exams database not loaded', 'results': []}), 500

        filtered_exams = filter_exams(cleaned_data, EXAMS_DATA)
        central_exams, state_exams = separate_exams_by_type(filtered_exams)

        return jsonify({
            'success': True,
            'results': filtered_exams,
            'central_exams': central_exams,
            'state_exams': state_exams,
            'total_count': len(filtered_exams),
            'central_count': len(central_exams),
            'state_count': len(state_exams)
        }), 200

    except Exception as e:
        logger.error(f"Error in /get-exams: {e}")
        return jsonify({'success': False, 'error': 'Server error', 'results': []}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'exams_loaded': len(EXAMS_DATA)
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if not EXAMS_DATA:
    EXAMS_DATA = load_exams_data()

if __name__ == '__main__':
    if not EXAMS_DATA:
        logger.warning("No exams data loaded!")
    logger.info("Starting GovCheck")
    app.run(debug=True, host='127.0.0.1', port=5000)