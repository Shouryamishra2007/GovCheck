# ═══════════════════════════════════════════════════════════════
# FEATURE 1: AI-Powered Opportunity Match Score Engine
# Purpose: Generate 0-100 match scores for every exam
# ═══════════════════════════════════════════════════════════════

import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class OpportunityScorer:
    """
    Produces semantic match scores combining:
    - Age compatibility (weighted 25%)
    - Education compatibility (weighted 35%)
    - State/category compatibility (weighted 25%)
    - Career alignment bonus (weighted 15%)
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_match_score(
        self,
        exam: Dict[str, Any],
        user_age: int,
        user_education: str,
        user_category: str,
        user_state: str
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Calculate comprehensive match score (0-100) with breakdown.
        
        Args:
            exam: Exam object from database
            user_age: User's age (int)
            user_education: Education level (10th, 12th, graduation, post-graduation)
            user_category: Category (general, obc, sc, st)
            user_state: State (e.g., 'haryana')
            
        Returns:
            Tuple[score, breakdown_dict]
        """

        scores = {
            'age': self._score_age_compatibility(exam, user_age),
            'education': self._score_education_compatibility(exam, user_education),
            'state_category': self._score_state_category(exam, user_state, user_category),
            'career_bonus': self._score_career_alignment(exam),
        }

        # Weighted sum: age(25%) + education(35%) + state_category(25%) + career(15%)
        total_score = (
            scores['age'] * 0.25 +
            scores['education'] * 0.35 +
            scores['state_category'] * 0.25 +
            scores['career_bonus'] * 0.15
        )

        return int(max(0, min(100, total_score))), scores

    def _score_age_compatibility(self, exam: Dict, user_age: int) -> float:
        """
        Score age eligibility: 0-100
        - 100 if perfectly in range
        - 70 if within upper extension
        - 40 if age relaxation possible
        - 0 if ineligible
        """
        min_age = exam.get('min_age', 18)
        max_age = exam.get('max_age')

        # Handle dict-based max_age (with category breakdowns)
        if isinstance(max_age, dict):
            max_age = max_age.get('General', list(max_age.values())[0] if max_age else 65)
        
        max_age = max_age or 65

        # Perfect range
        if min_age <= user_age <= max_age:
            return 100

        # Upper extension (within 2 years)
        if user_age <= max_age + 2:
            return 70

        # Age relaxation for categories (SC/ST get +5 years)
        if user_age <= max_age + 5:
            return 40

        return 0

    def _score_education_compatibility(self, exam: Dict, user_education: str) -> float:
        """
        Score education level match.
        - 100 if exam requires lower/equal education
        - 80 if exact match
        - 50 if overqualified (still eligible)
        - 0 if underqualified
        """
        required_education = exam.get('education_required', '10th')
        education_order = {
            '10th': 1,
            '12th': 2,
            'graduation': 3,
            'post-graduation': 4
        }

        user_level = education_order.get(user_education, 0)
        required_level = education_order.get(required_education, 1)

        if user_level == required_level:
            return 100  # Exact match
        elif user_level > required_level:
            return 80  # Overqualified (always eligible)
        else:
            return 0  # Underqualified

    def _score_state_category(self, exam: Dict, user_state: str, user_category: str) -> float:
        """
        Score state and category alignment.
        - 100 if exam is pan-India or covers state with category benefit
        - 80 if covers state but no category benefit
        - 60 if pan-India but no specific benefit
        - 40 if state-specific only
        - 0 if not applicable
        """
        coverage = exam.get('states', 'all')
        category_benefits = exam.get('category_benefits', {})

        # Pan-India exams
        if coverage == 'all' or coverage == 'All India':
            base = 80
        # State-specific
        elif isinstance(coverage, list):
            if user_state in coverage or user_state.replace('_', ' ').title() in coverage:
                base = 80
            else:
                return 0
        elif isinstance(coverage, str):
            if user_state in coverage.lower():
                base = 80
            else:
                return 0
        else:
            return 60

        # Bonus for category benefits
        if user_category in category_benefits:
            return 100  # Best score
        
        return base

    def _score_career_alignment(self, exam: Dict) -> float:
        """
        Bonus for career-relevant exams based on keyword matching.
        """
        exam_name = exam.get('name', '').lower()
        
        # High-value exams get bonus
        premium_exams = ['upsc', 'nda', 'ias', 'ifs', 'ips']
        if any(p in exam_name for p in premium_exams):
            return 100
        
        return 70

    def rank_exams(
        self,
        exams: List[Dict],
        user_profile: Dict
    ) -> List[Dict]:
        """
        Score and rank exams for user. Returns sorted list with scores attached.
        """
        scored_exams = []

        for exam in exams:
            score, breakdown = self.calculate_match_score(
                exam,
                user_profile['age'],
                user_profile['education'],
                user_profile['category'],
                user_profile['state']
            )

            scored_exams.append({
                **exam,
                'match_score': score,
                'score_breakdown': breakdown
            })

        # Sort by score descending
        return sorted(scored_exams, key=lambda x: x['match_score'], reverse=True)