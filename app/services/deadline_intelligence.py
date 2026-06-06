# ═══════════════════════════════════════════════════════════════
# FEATURE 6: Deadline Intelligence
# Provides visual urgency indicators
# ═══════════════════════════════════════════════════════════════

from datetime import datetime, timedelta
from typing import Dict, Tuple

class DeadlineIntelligence:
    """
    Calculate time-to-deadline and generate urgency indicators.
    """

    def __init__(self):
        pass

    def analyze_deadline(self, exam: Dict) -> Dict[str, any]:
        """
        Analyze deadline and return urgency status.
        
        Returns:
            {
                'status': 'urgent' | 'warning' | 'safe',
                'indicator': '🔴' | '🟡' | '🟢',
                'days_remaining': int,
                'message': str
            }
        """
        deadline_str = exam.get('application_deadline', '')
        
        if not deadline_str:
            return {
                'status': 'unknown',
                'indicator': '⭕',
                'days_remaining': None,
                'message': 'Deadline not specified'
            }

        try:
            # Parse deadline (assuming format: YYYY-MM-DD or similar)
            deadline = self._parse_date(deadline_str)
            if not deadline:
                return {
                    'status': 'unknown',
                    'indicator': '⭕',
                    'days_remaining': None,
                    'message': 'Deadline format unclear'
                }
            
            today = datetime.now()
            days_remaining = (deadline - today).days
            
            if days_remaining < 0:
                return {
                    'status': 'closed',
                    'indicator': '❌',
                    'days_remaining': 0,
                    'message': 'Application closed'
                }
            elif days_remaining < 3:
                return {
                    'status': 'urgent',
                    'indicator': '🔴',
                    'days_remaining': days_remaining,
                    'message': f'Apply within {days_remaining} days!'
                }
            elif days_remaining < 15:
                return {
                    'status': 'warning',
                    'indicator': '🟡',
                    'days_remaining': days_remaining,
                    'message': f'{days_remaining} days left'
                }
            else:
                return {
                    'status': 'safe',
                    'indicator': '🟢',
                    'days_remaining': days_remaining,
                    'message': f'{days_remaining} days left'
                }

        except Exception as e:
            return {
                'status': 'error',
                'indicator': '⚠',
                'days_remaining': None,
                'message': f'Error: {str(e)}'
            }

    def _parse_date(self, date_str: str):
        """Try multiple date formats."""
        formats = [
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%B %d, %Y',
            '%b %d, %Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None

    def attach_deadline_info(self, exams: list) -> list:
        """Add deadline info to all exams."""
        for exam in exams:
            exam['deadline_info'] = self.analyze_deadline(exam)
        return exams