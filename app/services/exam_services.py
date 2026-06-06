import json
import os
import logging
import re
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

EDU_ORDER = {'10th': 1, '12th': 2, 'graduation': 3, 'post-graduation': 4}


class ExamService:
    def __init__(self):
        self.exams: List[Dict] = []
        self._load()

    def _load(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'data', 'exams.json')
        path = os.path.normpath(path)
        try:
            with open(path, encoding='utf-8') as f:
                self.exams = json.load(f)
            logger.info(f"Loaded {len(self.exams)} exams")
        except Exception as e:
            logger.error(f"Could not load exams: {e}")
            self.exams = []

    @property
    def total_count(self) -> int:
        return len(self.exams)

    # ── Validation ──────────────────────────────────────────────────────────

    def validate(self, raw: dict) -> Tuple[bool, Optional[dict], Optional[str]]:
        age_str = str(raw.get('age', '')).strip()
        if not age_str:
            return False, None, "Age is required"
        try:
            age = int(age_str)
        except ValueError:
            return False, None, "Age must be a number"
        if not 10 <= age <= 60:
            return False, None, "Age must be between 10 and 60"

        status = raw.get('status', '').strip().lower()
        status_map = {
            '10th': '10th', '12th': '12th', '12': '12th',
            'graduate': 'graduation', 'graduation': 'graduation',
            'postgraduate': 'post-graduation', 'post-graduate': 'post-graduation',
            'post-graduation': 'post-graduation', 'pg': 'post-graduation'
        }
        if status not in status_map:
            return False, None, f"Invalid education status: {status}"
        status = status_map[status]

        category = raw.get('category', '').strip().lower()
        if category not in ('general', 'obc', 'sc', 'st'):
            return False, None, f"Invalid category: {category}"

        state = raw.get('state', '').strip().lower()
        if not state:
            return False, None, "State is required"

        return True, {'age': age, 'status': status, 'category': category, 'state': state}, None

    # ── Eligibility checks ──────────────────────────────────────────────────

    def _age_ok(self, age: int, category: str, exam: dict) -> Tuple[bool, int]:
        """Returns (eligible, age_score 0-100)."""
        min_age = exam.get('min_age', 0)
        max_data = exam.get('max_age', 120)
        cat_map = {'general': 'General', 'obc': 'OBC', 'sc': 'SC', 'st': 'ST'}

        if isinstance(max_data, dict):
            max_age = max_data.get(cat_map.get(category, 'General'),
                                   max_data.get('General', 120))
        else:
            max_age = int(max_data)

        if not (min_age <= age <= max_age):
            return False, 0

        # Score: perfect if in sweet spot (25-75% of range), taper near edges
        span = max_age - min_age or 1
        position = (age - min_age) / span
        age_score = int(100 - abs(position - 0.5) * 40)
        return True, age_score

    def _edu_ok(self, status: str, exam: dict) -> Tuple[bool, int]:
        required = exam.get('eligibility', [])
        if not required or 'all' in required:
            return True, 100
        user_level = EDU_ORDER.get(status, 0)
        for edu in required:
            req_level = EDU_ORDER.get(edu.lower().strip(), 0)
            if user_level >= req_level > 0:
                overshoot = user_level - req_level
                score = max(70, 100 - overshoot * 10)
                return True, score
        return False, 0

    def _state_ok(self, state: str, exam: dict) -> Tuple[bool, int]:
        if state in ('all', 'national', ''):
            return True, 80

        govt_type = exam.get('govt_type', '').upper()
        if 'CENTRAL' in govt_type or 'UNION TERRITORY' in govt_type:
            return True, 90

        exam_states = exam.get('states', [])

        def norm(s): return s.lower().strip().replace('_', ' ')

        if isinstance(exam_states, str):
            if norm(exam_states) == 'all':
                return True, 80
            return (norm(state) == norm(exam_states)), (100 if norm(state) == norm(exam_states) else 0)

        if isinstance(exam_states, list):
            normalized = [norm(s) for s in exam_states]
            if 'all' in normalized:
                return True, 80
            return (norm(state) in normalized), (100 if norm(state) in normalized else 0)

        return True, 80

    # ── Scoring ─────────────────────────────────────────────────────────────

    def _score(self, user: dict, exam: dict) -> int:
        _, age_s = self._age_ok(user['age'], user['category'], exam)
        _, edu_s = self._edu_ok(user['status'], exam)
        _, state_s = self._state_ok(user['state'], exam)

        # Weights: age 40%, edu 35%, state 25%
        return int(age_s * 0.40 + edu_s * 0.35 + state_s * 0.25)

    # ── Filter ───────────────────────────────────────────────────────────────

    def filter(self, user: dict) -> List[Dict]:
        results = []
        for exam in self.exams:
            try:
                age_ok, _ = self._age_ok(user['age'], user['category'], exam)
                edu_ok, _ = self._edu_ok(user['status'], exam)
                state_ok, _ = self._state_ok(user['state'], exam)
                if age_ok and edu_ok and state_ok:
                    exam_copy = dict(exam)
                    exam_copy['match_score'] = self._score(user, exam)
                    exam_copy['verified'] = self._verify_link(exam.get('official_link', ''))
                    results.append(exam_copy)
            except Exception as e:
                logger.warning(f"Error checking {exam.get('name')}: {e}")

        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results

    # ── Search ───────────────────────────────────────────────────────────────

    def search(self, query: str) -> List[Dict]:
        q = query.lower().strip()
        if not q:
            return []
        results = []
        for exam in self.exams:
            text = ' '.join([
                exam.get('name', ''),
                exam.get('description', ''),
                exam.get('conducting_type', ''),
                exam.get('govt_type', ''),
                ' '.join(exam.get('group', []) if isinstance(exam.get('group'), list) else [])
            ]).lower()
            if q in text or any(q in word for word in text.split()):
                exam_copy = dict(exam)
                exam_copy['verified'] = self._verify_link(exam.get('official_link', ''))
                results.append(exam_copy)
        return results[:20]

    # ── Analytics ────────────────────────────────────────────────────────────

    def analytics(self) -> dict:
        central = sum(1 for e in self.exams
                      if 'CENTRAL' in e.get('govt_type', '').upper()
                      or 'UNION TERRITORY' in e.get('govt_type', '').upper())
        state = self.total_count - central
        by_edu = {}
        for e in self.exams:
            for edu in (e.get('eligibility') or []):
                by_edu[edu] = by_edu.get(edu, 0) + 1
        conductors = {}
        for e in self.exams:
            c = e.get('conducting_type', 'Other')
            conductors[c] = conductors.get(c, 0) + 1
        top_conductors = sorted(conductors.items(), key=lambda x: -x[1])[:5]
        return {
            'total': self.total_count,
            'central': central,
            'state': state,
            'by_education': by_edu,
            'top_conductors': [{'name': k, 'count': v} for k, v in top_conductors]
        }

    # ── URL Verification ─────────────────────────────────────────────────────

    @staticmethod
    def _verify_link(url: str) -> bool:
        if not url:
            return False
        trusted = ('.gov.in', '.nic.in', '.gov', '.mil')
        return any(url.lower().split('?')[0].rstrip('/').endswith(t) for t in trusted)

    def separate(self, exams: list) -> Tuple[list, list]:
        central, state = [], []
        for e in exams:
            gt = e.get('govt_type', '').upper()
            if 'CENTRAL' in gt or 'UNION TERRITORY' in gt:
                central.append(e)
            else:
                state.append(e)
        return central, state
