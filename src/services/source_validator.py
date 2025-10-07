"""
Advanced source validation service with AI analysis
"""
import logging
from typing import List, Dict, Any, Optional
import requests
from requests.exceptions import RequestException, Timeout
from bs4 import BeautifulSoup

from ..api.models.sources import (
    SourceItem,
    AdvancedSourceValidationResult
)
from ..utils.tfidf_analyzer import TfidfAnalyzer
from ..utils.credibility_checker import CredibilityChecker

logger = logging.getLogger(__name__)


class SourceValidationService:
    """Service for advanced source validation with AI analysis"""
    
    def __init__(
        self,
        min_relevance: float = 0.7,
        min_credibility: float = 80.0,
        timeout: int = 10
    ):
        """
        Initialize source validation service
        
        Args:
            min_relevance: Minimum relevance score threshold
            min_credibility: Minimum credibility score threshold
            timeout: Request timeout in seconds
        """
        self.min_relevance = min_relevance
        self.min_credibility = min_credibility
        self.timeout = timeout
        self.tfidf_analyzer = TfidfAnalyzer()
        self.credibility_checker = CredibilityChecker()
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with proper headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'BookGen Academic Research Bot 1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        return session
    
    def validate_sources(
        self,
        biography_topic: str,
        sources_list: List[SourceItem],
        check_accessibility: bool = True
    ) -> Dict[str, Any]:
        """
        Validate sources with advanced analysis
        
        Args:
            biography_topic: Biography topic or character name
            sources_list: List of sources to validate
            check_accessibility: Whether to check URL accessibility
            
        Returns:
            Validation results dictionary
        """
        results = []
        total_relevance = 0.0
        total_credibility = 0.0
        valid_count = 0
        rejected_count = 0
        
        for source in sources_list:
            result = self.validate_single_source(
                source,
                biography_topic,
                check_accessibility
            )
            results.append(result)
            
            if result.is_valid:
                valid_count += 1
            
            # Track rejected sources (low relevance or credibility)
            if result.relevance_score is not None and result.relevance_score < self.min_relevance:
                rejected_count += 1
            elif result.credibility_score is not None and result.credibility_score < self.min_credibility:
                rejected_count += 1
            
            # Accumulate scores for averages
            if result.relevance_score is not None:
                total_relevance += result.relevance_score
            if result.credibility_score is not None:
                total_credibility += result.credibility_score
        
        # Calculate averages
        num_sources = len(sources_list)
        avg_relevance = total_relevance / num_sources if num_sources > 0 else 0.0
        avg_credibility = total_credibility / num_sources if num_sources > 0 else 0.0
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            results,
            avg_relevance,
            avg_credibility
        )
        
        return {
            'total_sources': num_sources,
            'valid_sources': valid_count,
            'invalid_sources': num_sources - valid_count,
            'rejected_sources': rejected_count,
            'average_relevance': round(avg_relevance, 3),
            'average_credibility': round(avg_credibility, 2),
            'results': results,
            'recommendations': recommendations
        }
    
    def validate_single_source(
        self,
        source: SourceItem,
        biography_topic: str,
        check_accessibility: bool = True
    ) -> AdvancedSourceValidationResult:
        """
        Validate a single source with advanced analysis
        
        Args:
            source: Source to validate
            biography_topic: Biography topic
            check_accessibility: Whether to check URL accessibility
            
        Returns:
            Advanced validation result
        """
        issues = []
        warnings = []
        metadata = {}
        is_accessible = None
        relevance_score = None
        credibility_score = None
        domain_category = None
        is_trusted = None
        
        # Basic validation
        if not source.title or len(source.title.strip()) == 0:
            issues.append("Title is empty or missing")
        
        # Check credibility
        credibility_info = self.credibility_checker.check_source_credibility(
            url=source.url,
            title=source.title,
            author=source.author,
            publication_date=source.publication_date
        )
        
        credibility_score = credibility_info["credibility_score"]
        domain_category = credibility_info.get("domain_category")
        is_trusted = credibility_info.get("is_trusted", False)
        
        # Add credibility issues and warnings
        issues.extend(credibility_info.get("issues", []))
        warnings.extend(credibility_info.get("warnings", []))
        
        # Store credibility metadata
        metadata["domain_score"] = credibility_info.get("domain_score")
        metadata["recency_score"] = credibility_info.get("recency_score")
        metadata["completeness_score"] = credibility_info.get("completeness_score")
        
        if credibility_info.get("years_old"):
            metadata["years_old"] = credibility_info["years_old"]
        
        # Check URL if present
        if source.url and check_accessibility:
            try:
                # Fetch content for relevance analysis
                response = self.session.get(
                    source.url,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                is_accessible = response.status_code < 400
                
                if is_accessible:
                    # Extract content
                    content = self._extract_text_from_html(response.text)
                    
                    # Calculate relevance score
                    relevance_score = self.tfidf_analyzer.calculate_relevance_with_mentions(
                        character_name=biography_topic,
                        source_title=source.title,
                        content=content
                    )
                    
                    metadata["content_length"] = len(content)
                    metadata["content_type"] = response.headers.get("content-type", "unknown")
                    
                    # Check if generic page
                    if self._is_generic_page(response.text):
                        warnings.append("Page appears to be generic (search, home, etc.)")
                        relevance_score = max(0.0, relevance_score - 0.3)
                    
                else:
                    issues.append(f"URL not accessible (status code: {response.status_code})")
                    
            except Timeout:
                is_accessible = False
                issues.append("URL request timed out")
            except RequestException as e:
                is_accessible = False
                issues.append(f"URL not accessible: {str(e)}")
        
        # Determine if source is valid
        is_valid = len(issues) == 0
        
        # Additional validation based on scores
        if relevance_score is not None and relevance_score < self.min_relevance:
            warnings.append(f"Relevance score ({relevance_score:.2f}) below threshold ({self.min_relevance})")
        
        if credibility_score is not None and credibility_score < self.min_credibility:
            warnings.append(f"Credibility score ({credibility_score:.1f}) below threshold ({self.min_credibility})")
        
        return AdvancedSourceValidationResult(
            source=source,
            is_valid=is_valid,
            is_accessible=is_accessible,
            relevance_score=relevance_score,
            credibility_score=credibility_score,
            domain_category=domain_category,
            is_trusted=is_trusted,
            issues=issues,
            warnings=warnings,
            metadata=metadata if metadata else None
        )
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """
        Extract clean text from HTML content
        
        Args:
            html_content: HTML content
            
        Returns:
            Extracted text
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.warning(f"Error extracting text from HTML: {e}")
            return ""
    
    def _is_generic_page(self, html_content: str) -> bool:
        """
        Check if page is generic (home, search, etc.)
        
        Args:
            html_content: HTML content
            
        Returns:
            True if generic page
        """
        import re
        
        generic_indicators = [
            r'<title>[^<]*search[^<]*</title>',
            r'<title>[^<]*home[^<]*</title>',
            r'<title>[^<]*welcome[^<]*</title>',
            r'class=["\']search-results["\']',
            r'class=["\']homepage["\']',
            r'id=["\']search-form["\']',
            r'no results found',
            r'page not found',
            r'404 error'
        ]
        
        content_lower = html_content.lower()
        return any(re.search(pattern, content_lower, re.IGNORECASE) for pattern in generic_indicators)
    
    def _generate_recommendations(
        self,
        results: List[AdvancedSourceValidationResult],
        avg_relevance: float,
        avg_credibility: float
    ) -> List[str]:
        """
        Generate recommendations for improving source quality
        
        Args:
            results: Validation results
            avg_relevance: Average relevance score
            avg_credibility: Average credibility score
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check average relevance
        if avg_relevance < 0.7:
            recommendations.append(
                f"Average relevance score ({avg_relevance:.2f}) is below recommended threshold (0.7). "
                "Consider finding more topic-specific sources."
            )
        
        # Check average credibility
        if avg_credibility < 80.0:
            recommendations.append(
                f"Average credibility score ({avg_credibility:.1f}) is below recommended threshold (80). "
                "Consider using more trusted academic or government sources."
            )
        
        # Count trusted vs untrusted sources
        trusted_count = sum(1 for r in results if r.is_trusted)
        untrusted_count = len(results) - trusted_count
        
        if untrusted_count > trusted_count:
            recommendations.append(
                f"More untrusted sources ({untrusted_count}) than trusted sources ({trusted_count}). "
                "Consider replacing with sources from academic institutions or reputable publications."
            )
        
        # Check for missing metadata
        missing_authors = sum(1 for r in results if not r.source.author)
        missing_dates = sum(1 for r in results if not r.source.publication_date)
        
        if missing_authors > len(results) * 0.5:
            recommendations.append(
                f"{missing_authors} sources are missing author information. "
                "Add author information to improve source credibility."
            )
        
        if missing_dates > len(results) * 0.5:
            recommendations.append(
                f"{missing_dates} sources are missing publication dates. "
                "Add publication dates to assess source recency."
            )
        
        # Check for inaccessible URLs
        inaccessible = sum(1 for r in results if r.is_accessible is False)
        if inaccessible > 0:
            recommendations.append(
                f"{inaccessible} source URLs are not accessible. "
                "Verify URLs or find alternative sources."
            )
        
        if not recommendations:
            recommendations.append("Source quality is good. No major improvements needed.")
        
        return recommendations
