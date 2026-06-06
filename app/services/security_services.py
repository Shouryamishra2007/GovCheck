# ═══════════════════════════════════════════════════════════════
# FEATURE 5: Cybersecurity-focused Source Verification
# ═══════════════════════════════════════════════════════════════

import logging
from urllib.parse import urlparse
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class SourceVerifier:
    """
    Verify government notification sources for cybersecurity.
    Protects users from phishing and fake job sites.
    """

    # Trusted government domains
    TRUSTED_DOMAINS = {
        'gov.in': 'Government of India Official',
        'nic.in': 'National Informatics Centre',
        'ias.ac.in': 'Indian Administrative Service',
        'upsc.gov.in': 'UPSC Official',
        'ssc.nic.in': 'SSC Official',
        'rrbonline.gov.in': 'Railway Board',
        'ibps.in': 'IBPS',
        'sbi.co.in': 'SBI',
        'defence.gov.in': 'Defence Ministry',
        'mhrd.gov.in': 'Ministry of Education',
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def verify_source(self, url: str) -> Tuple[bool, str, str]:
        """
        Verify if URL is from a trusted government source.
        
        Returns:
            (is_verified: bool, status: str, domain: str)
            - is_verified: True if from trusted domain
            - status: Human-readable status message
            - domain: Extracted domain
        """
        if not url or not isinstance(url, str):
            return False, "Invalid URL", ""

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')
            
            # Check against trusted domains
            for trusted_domain, description in self.TRUSTED_DOMAINS.items():
                if domain.endswith(trusted_domain):
                    return True, f"✓ Verified: {description}", domain
            
            # Suspicious patterns
            if self._is_suspicious(domain, url):
                return False, "⚠ Warning: Unverified source", domain
            
            return False, "⚠ Verify: Not from official gov.in domain", domain

        except Exception as e:
            self.logger.error(f"Verification error: {str(e)}")
            return False, "Error verifying source", ""

    def _is_suspicious(self, domain: str, url: str) -> bool:
        """
        Detect suspicious patterns:
        - Typosquatting (upcs.gov.in instead of upsc.gov.in)
        - Mixed-case domains
        - Shortened URLs
        """
        suspicious_patterns = [
            '.tk', '.ml', '.ga',  # Free domains
            'bit.ly', 'tinyurl',   # URL shorteners
            'job', 'recruitment',  # Generic job keywords
        ]
        
        # Check for suspicious TLDs
        if any(url.endswith(p) for p in suspicious_patterns):
            return True
        
        # Check for typosquatting: compare against trusted domains
        for trusted in self.TRUSTED_DOMAINS.keys():
            if self._is_typosquat(domain, trusted):
                return True
        
        return False

    def _is_typosquat(self, suspect: str, trusted: str) -> bool:
        """Detect typosquatting using string similarity."""
        # Simple check: if 1-2 characters different, flag as suspicious
        if len(suspect) == len(trusted):
            diff_count = sum(1 for a, b in zip(suspect, trusted) if a != b)
            return 0 < diff_count <= 2
        return False

    def add_verification_badge(self, exam: Dict) -> Dict:
        """Attach verification info to exam object."""
        link = exam.get('official_link', '')
        
        if link:
            is_verified, status, domain = self.verify_source(link)
            exam['verified'] = is_verified
            exam['verification_status'] = status
            exam['source_domain'] = domain
        else:
            exam['verified'] = False
            exam['verification_status'] = '? No official link'
            exam['source_domain'] = ''
        
        return exam