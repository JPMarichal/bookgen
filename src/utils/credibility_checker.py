"""
Credibility checker for source validation
"""
import re
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from datetime import datetime
from dateutil import parser as date_parser

from ..config.trusted_domains import (
    get_domain_credibility_score,
    is_trusted_domain,
    get_domain_category
)


class CredibilityChecker:
    """Checker for source credibility and quality"""
    
    def __init__(self):
        """Initialize credibility checker"""
        pass
    
    def check_source_credibility(
        self,
        url: Optional[str],
        title: str,
        author: Optional[str] = None,
        publication_date: Optional[str] = None,
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive credibility check for a source
        
        Args:
            url: Source URL
            title: Source title
            author: Source author
            publication_date: Publication date
            content: Page content (if available)
            
        Returns:
            Dictionary with credibility analysis
        """
        result = {
            "credibility_score": 50.0,  # Default neutral score
            "domain_score": 50.0,
            "recency_score": 50.0,
            "completeness_score": 50.0,
            "domain_category": "other",
            "is_trusted": False,
            "issues": [],
            "warnings": []
        }
        
        # Check domain credibility
        if url:
            domain_info = self._check_domain_credibility(url)
            result["domain_score"] = domain_info["score"]
            result["domain_category"] = domain_info["category"]
            result["is_trusted"] = domain_info["is_trusted"]
            
            if not domain_info["is_trusted"]:
                result["warnings"].append(f"Domain is not in trusted list (category: {domain_info['category']})")
        
        # Check recency
        if publication_date:
            recency_info = self._check_recency(publication_date)
            result["recency_score"] = recency_info["score"]
            result["years_old"] = recency_info.get("years_old")
            
            if recency_info.get("warnings"):
                result["warnings"].extend(recency_info["warnings"])
        
        # Check completeness
        completeness_info = self._check_completeness(title, author, publication_date, url)
        result["completeness_score"] = completeness_info["score"]
        
        if completeness_info.get("issues"):
            result["issues"].extend(completeness_info["issues"])
        
        # Calculate overall credibility score
        result["credibility_score"] = self._calculate_overall_credibility(
            result["domain_score"],
            result["recency_score"],
            result["completeness_score"]
        )
        
        return result
    
    def _check_domain_credibility(self, url: str) -> Dict[str, Any]:
        """
        Check domain credibility
        
        Args:
            url: URL to check
            
        Returns:
            Domain credibility information
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Remove 'www.' prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            score = get_domain_credibility_score(domain)
            category = get_domain_category(domain)
            is_trusted = is_trusted_domain(domain)
            
            return {
                "domain": domain,
                "score": score,
                "category": category,
                "is_trusted": is_trusted
            }
            
        except Exception:
            return {
                "domain": "unknown",
                "score": 30.0,
                "category": "other",
                "is_trusted": False
            }
    
    def _check_recency(self, publication_date: str) -> Dict[str, Any]:
        """
        Check recency of publication
        
        Args:
            publication_date: Publication date string
            
        Returns:
            Recency information
        """
        result = {
            "score": 50.0,
            "warnings": []
        }
        
        try:
            # Parse date
            parsed_date = date_parser.parse(publication_date)
            current_date = datetime.now()
            
            # Calculate age in years
            years_old = (current_date - parsed_date).days / 365.25
            result["years_old"] = round(years_old, 1)
            
            # Score based on age
            if years_old < 5:
                result["score"] = 100.0
            elif years_old < 10:
                result["score"] = 90.0
            elif years_old < 20:
                result["score"] = 75.0
            elif years_old < 50:
                result["score"] = 60.0
            else:
                result["score"] = 40.0
                result["warnings"].append(f"Source is {result['years_old']} years old - may contain outdated information")
            
        except Exception:
            result["warnings"].append("Could not parse publication date")
        
        return result
    
    def _check_completeness(
        self,
        title: str,
        author: Optional[str],
        publication_date: Optional[str],
        url: Optional[str]
    ) -> Dict[str, Any]:
        """
        Check completeness of source metadata
        
        Args:
            title: Source title
            author: Source author
            publication_date: Publication date
            url: Source URL
            
        Returns:
            Completeness information
        """
        result = {
            "score": 0.0,
            "issues": []
        }
        
        score = 0
        max_score = 4
        
        # Title (required)
        if title and len(title.strip()) > 0:
            score += 1
        else:
            result["issues"].append("Missing or empty title")
        
        # Author (optional but valuable)
        if author and len(author.strip()) > 0:
            score += 1
        else:
            result["issues"].append("Missing author information")
        
        # Publication date (optional but valuable)
        if publication_date:
            score += 1
        else:
            result["issues"].append("Missing publication date")
        
        # URL (optional but valuable)
        if url:
            score += 1
        
        result["score"] = (score / max_score) * 100.0
        
        return result
    
    def _calculate_overall_credibility(
        self,
        domain_score: float,
        recency_score: float,
        completeness_score: float
    ) -> float:
        """
        Calculate overall credibility score
        
        Args:
            domain_score: Domain credibility score
            recency_score: Recency score
            completeness_score: Completeness score
            
        Returns:
            Overall credibility score (0-100)
        """
        # Weighted average: domain is most important, then completeness, then recency
        weights = {
            "domain": 0.5,
            "completeness": 0.3,
            "recency": 0.2
        }
        
        overall = (
            domain_score * weights["domain"] +
            completeness_score * weights["completeness"] +
            recency_score * weights["recency"]
        )
        
        return round(overall, 2)
    
    def is_academic_format(
        self,
        title: str,
        author: Optional[str],
        publication_date: Optional[str]
    ) -> bool:
        """
        Check if source follows academic format
        
        Args:
            title: Source title
            author: Source author
            publication_date: Publication date
            
        Returns:
            True if academic format
        """
        # Academic sources typically have:
        # 1. A clear title
        # 2. Author(s)
        # 3. Publication date
        
        has_title = bool(title and len(title.strip()) > 0)
        has_author = bool(author and len(author.strip()) > 0)
        has_date = bool(publication_date)
        
        # At least title and one of (author or date)
        return has_title and (has_author or has_date)
