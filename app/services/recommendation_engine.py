# ═══════════════════════════════════════════════════════════════
# FEATURE 9: Career Roadmap Generator
# Generates educational and career pathways
# ═══════════════════════════════════════════════════════════════

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class CareerRoadmapGenerator:
    """
    Generate career pathways based on education level and goals.
    """

    ROADMAP_TEMPLATES = {
        '12th_engineering': {
            'title': 'Engineering → Civil Services Pathway',
            'steps': [
                {
                    'stage': 1,
                    'education': 'B.Tech (4 years)',
                    'focus': 'Electrical/Mechanical/Civil Engineering',
                    'exams': ['GATE', 'ESE (Engineering Services)'],
                },
                {
                    'stage': 2,
                    'education': 'GATE/ESE Qualification',
                    'focus': 'Government Engineering Service',
                    'exams': ['ESE Written + Interview'],
                },
                {
                    'stage': 3,
                    'education': 'M.Tech or PSU Job',
                    'focus': 'Research or Industry',
                    'exams': ['UPSC', 'Public Sector Units'],
                },
                {
                    'stage': 4,
                    'career': 'IES/Scientist/Government Officer',
                    'salary_range': '₹50,000 - ₹2,00,000/month',
                },
            ]
        },
        '12th_general': {
            'title': '12th Pass → IAS/Civil Services',
            'steps': [
                {
                    'stage': 1,
                    'education': 'Bachelor\'s Degree (3 years)',
                    'focus': 'Any stream - humanities/commerce/science',
                    'exams': ['College entrance exams'],
                },
                {
                    'stage': 2,
                    'education': 'Graduation Complete',
                    'focus': 'UPSC Preparation',
                    'exams': ['UPSC Prelims'],
                },
                {
                    'stage': 3,
                    'education': 'Prelims Success',
                    'focus': 'UPSC Mains',
                    'exams': ['UPSC Mains (9 papers)'],
                },
                {
                    'stage': 4,
                    'career': 'IAS/IFS/IPS Officer',
                    'salary_range': '₹60,000 - ₹2,50,000/month',
                },
            ]
        },
        'graduation_tech': {
            'title': 'B.Tech → Tech + Admin Careers',
            'steps': [
                {
                    'stage': 1,
                    'path': 'Option A: Public Sector',
                    'exams': ['ISRO', 'BARC', 'DRDO', 'Defence R&D'],
                    'salary': '₹70,000 - ₹3,00,000/month',
                },
                {
                    'stage': 1,
                    'path': 'Option B: Administration',
                    'exams': ['UPSC (technical category)', 'SSC Engineering'],
                    'salary': '₹60,000 - ₹2,50,000/month',
                },
                {
                    'stage': 2,
                    'education': 'M.Tech (if pursuing Option A)',
                    'exams': ['GATE', 'PSU selection'],
                },
            ]
        },
        'graduation_nontech': {
            'title': 'B.A/B.Com → Admin & Banking',
            'steps': [
                {
                    'stage': 1,
                    'path': 'Banking Sector',
                    'exams': ['IBPS Clerk', 'IBPS PO', 'SBI'],
                    'salary': '₹30,000 - ₹1,50,000/month',
                },
                {
                    'stage': 2,
                    'path': 'Administrative Services',
                    'exams': ['UPSC', 'State PSC', 'SSC CGL'],
                    'salary': '₹60,000 - ₹2,50,000/month',
                },
                {
                    'stage': 3,
                    'path': 'Specialized Services',
                    'exams': ['IFS (Foreign Service)', 'IPolS', 'Central Secretariat Service'],
                    'salary': '₹80,000 - ₹3,00,000/month',
                },
            ]
        },
    }

    def generate_roadmap(self, education: str, specialization: str = None) -> Dict:
        """
        Generate a career roadmap based on education level.
        
        Args:
            education: '10th', '12th', 'graduation', 'post-graduation'
            specialization: 'engineering', 'tech', 'commerce', 'general', etc.
        
        Returns:
            Roadmap dict with steps and opportunities
        """
        
        # Select template
        if education == '12th' and specialization == 'engineering':
            template_key = '12th_engineering'
        elif education == '12th':
            template_key = '12th_general'
        elif education == 'graduation' and specialization == 'engineering':
            template_key = 'graduation_tech'
        elif education == 'graduation':
            template_key = 'graduation_nontech'
        else:
            return {'error': 'Roadmap not available for this profile'}
        
        template = self.ROADMAP_TEMPLATES.get(template_key, {})
        
        return {
            'success': True,
            'roadmap': template,
            'key_milestones': len(template.get('steps', [])),
        }

    def get_all_roadmaps(self) -> List[Dict]:
        """Get all available roadmaps for frontend display."""
        return [
            {
                'key': k,
                'title': v.get('title', k),
                'steps': len(v.get('steps', []))
            }
            for k, v in self.ROADMAP_TEMPLATES.items()
        ]