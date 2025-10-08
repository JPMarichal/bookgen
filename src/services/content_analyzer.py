"""
Advanced Content Analyzer
AI-powered content analysis for source quality evaluation
"""
import logging
import re
import json
from typing import Optional, Dict, Any
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from ..services.openrouter_client import OpenRouterClient, OpenRouterException
from ..api.models.content_analysis import (
    BiographicalDepthAnalysis,
    FactualAccuracyAnalysis,
    BiasAnalysis,
    ContentQualityScore
)

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """Advanced content analyzer using AI for quality evaluation"""
    
    def __init__(self, openrouter_client: Optional[OpenRouterClient] = None):
        """
        Initialize content analyzer
        
        Args:
            openrouter_client: Optional OpenRouter client instance
        """
        self.openrouter_client = openrouter_client or OpenRouterClient()
        
        # Quality models for different analysis types
        self.quality_models = {
            'content_depth': 'anthropic/claude-3.5-sonnet',
            'factual_accuracy': 'openai/gpt-4o-mini',
            'biographical_relevance': 'google/gemini-pro-1.5'
        }
        
        logger.info("ContentAnalyzer initialized with AI models")
    
    def analyze_source_content_quality(
        self,
        source_url: str,
        character: str,
        max_content_length: int = 10000
    ) -> ContentQualityScore:
        """
        Analyze source content quality using AI
        
        Args:
            source_url: URL of the source to analyze
            character: Character/person name for biographical analysis
            max_content_length: Maximum content length to analyze
            
        Returns:
            ContentQualityScore with comprehensive analysis
            
        Raises:
            Exception: If analysis fails
        """
        logger.info(f"Analyzing content quality for {source_url} about {character}")
        
        try:
            # 1. Fetch and clean content
            raw_content = self._fetch_and_clean_content(source_url, max_content_length)
            
            if not raw_content or len(raw_content) < 100:
                logger.warning(f"Insufficient content from {source_url}")
                return self._create_default_score()
            
            # 2. Analyze biographical depth
            depth_analysis = self._analyze_biographical_depth(raw_content, character)
            
            # 3. Verify factual accuracy
            factual_analysis = self._verify_factual_accuracy(raw_content, character)
            
            # 4. Calculate information density
            information_density = self._calculate_information_density(raw_content, character)
            
            # 5. Analyze bias and neutrality
            bias_analysis = self._analyze_bias_and_neutrality(raw_content)
            
            # 6. Calculate content uniqueness
            content_uniqueness = self._calculate_uniqueness_score(raw_content, character)
            
            # Create comprehensive score
            score = ContentQualityScore(
                biographical_depth=depth_analysis.depth_score,
                factual_accuracy=factual_analysis.accuracy_score,
                information_density=information_density,
                neutrality_score=bias_analysis.neutrality_score,
                source_citations=factual_analysis.citation_count,
                content_uniqueness=content_uniqueness,
                metadata={
                    'content_length': len(raw_content),
                    'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                    'depth_details': depth_analysis.model_dump(),
                    'factual_details': factual_analysis.model_dump(),
                    'bias_details': bias_analysis.model_dump()
                }
            )
            
            # Calculate overall score
            score.overall_score = score.calculate_overall_score()
            
            logger.info(
                f"Content analysis complete: "
                f"overall={score.overall_score:.2f}, "
                f"depth={score.biographical_depth:.2f}, "
                f"accuracy={score.factual_accuracy:.2f}"
            )
            
            return score
            
        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            raise
    
    def _fetch_and_clean_content(self, url: str, max_length: int) -> str:
        """
        Fetch and clean content from URL
        
        Args:
            url: URL to fetch
            max_length: Maximum content length
            
        Returns:
            Cleaned content text
        """
        try:
            logger.debug(f"Fetching content from {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; BookGenBot/1.0; +https://bookgen.ai)'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Truncate to max length
            if len(text) > max_length:
                text = text[:max_length]
            
            logger.debug(f"Fetched {len(text)} characters from {url}")
            return text
            
        except Exception as e:
            logger.error(f"Failed to fetch content from {url}: {str(e)}")
            return ""
    
    def _analyze_biographical_depth(
        self,
        content: str,
        character: str
    ) -> BiographicalDepthAnalysis:
        """
        Analyze biographical depth using AI
        
        Args:
            content: Content to analyze
            character: Character name
            
        Returns:
            BiographicalDepthAnalysis
        """
        logger.debug(f"Analyzing biographical depth for {character}")
        
        try:
            # Prepare prompt for AI
            prompt = f"""Analyze the biographical depth of the following content about {character}.

Rate each aspect on a scale of 0-100:
1. Early life and formation coverage
2. Professional development and major achievements
3. Historical and social context
4. Personal relationships and influences
5. Legacy and historical impact
6. Specificity (specific details vs generalities)
7. Use of concrete dates, places, and names

Content to analyze (first 2000 chars):
{content[:2000]}

Respond with a JSON object containing:
- early_life_coverage (0-100)
- professional_development (0-100)
- historical_context (0-100)
- personal_relationships (0-100)
- legacy_impact (0-100)
- specificity_score (0-100)
- concrete_details (0-100)
- justification (brief text explanation)

Calculate depth_score as the average of all scores divided by 100 (0-1 range).
"""
            
            # Call AI with low temperature for consistency
            response = self.openrouter_client.generate_text(
                prompt=prompt,
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse JSON response
            try:
                # Extract JSON from response (may have markdown formatting)
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                else:
                    data = json.loads(response)
                
                # Calculate depth score
                scores = [
                    data.get('early_life_coverage', 0),
                    data.get('professional_development', 0),
                    data.get('historical_context', 0),
                    data.get('personal_relationships', 0),
                    data.get('legacy_impact', 0),
                    data.get('specificity_score', 0),
                    data.get('concrete_details', 0)
                ]
                depth_score = sum(scores) / (len(scores) * 100)
                
                return BiographicalDepthAnalysis(
                    depth_score=depth_score,
                    early_life_coverage=data.get('early_life_coverage', 0),
                    professional_development=data.get('professional_development', 0),
                    historical_context=data.get('historical_context', 0),
                    personal_relationships=data.get('personal_relationships', 0),
                    legacy_impact=data.get('legacy_impact', 0),
                    specificity_score=data.get('specificity_score', 0),
                    concrete_details=data.get('concrete_details', 0),
                    justification=data.get('justification', 'AI analysis completed')
                )
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse AI response: {e}, using defaults")
                # Return default analysis
                return BiographicalDepthAnalysis(
                    depth_score=0.5,
                    justification="Failed to parse AI response, using default scores"
                )
                
        except OpenRouterException as e:
            logger.error(f"AI analysis failed: {str(e)}")
            # Return default analysis on error
            return BiographicalDepthAnalysis(
                depth_score=0.5,
                justification=f"AI analysis error: {str(e)}"
            )
    
    def _verify_factual_accuracy(
        self,
        content: str,
        character: str
    ) -> FactualAccuracyAnalysis:
        """
        Verify factual accuracy using AI
        
        Args:
            content: Content to analyze
            character: Character name
            
        Returns:
            FactualAccuracyAnalysis
        """
        logger.debug(f"Verifying factual accuracy for {character}")
        
        try:
            prompt = f"""Analyze the factual accuracy of the following content about {character}.

Evaluate:
1. Number of citations or references
2. Number of verifiable factual statements
3. Number of questionable or unverified claims
4. Accuracy of dates mentioned (0-100)
5. Internal consistency of facts (0-100)

Content to analyze (first 2000 chars):
{content[:2000]}

Respond with a JSON object containing:
- citation_count (integer)
- verifiable_facts (integer)
- questionable_claims (integer)
- date_accuracy (0-100)
- consistency_score (0-100)
- justification (brief explanation)

Calculate accuracy_score (0-1) based on the ratio of verifiable facts to questionable claims,
considering date accuracy and consistency.
"""
            
            response = self.openrouter_client.generate_text(
                prompt=prompt,
                temperature=0.1,
                max_tokens=800
            )
            
            try:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                else:
                    data = json.loads(response)
                
                # Calculate accuracy score
                verifiable = data.get('verifiable_facts', 0)
                questionable = data.get('questionable_claims', 0)
                total = verifiable + questionable
                
                if total > 0:
                    fact_ratio = verifiable / total
                else:
                    fact_ratio = 0.5
                
                date_acc = data.get('date_accuracy', 50) / 100
                consistency = data.get('consistency_score', 50) / 100
                
                accuracy_score = (fact_ratio * 0.5 + date_acc * 0.25 + consistency * 0.25)
                
                return FactualAccuracyAnalysis(
                    accuracy_score=accuracy_score,
                    citation_count=data.get('citation_count', 0),
                    verifiable_facts=data.get('verifiable_facts', 0),
                    questionable_claims=data.get('questionable_claims', 0),
                    date_accuracy=data.get('date_accuracy', 50),
                    consistency_score=data.get('consistency_score', 50),
                    justification=data.get('justification', 'AI analysis completed')
                )
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse AI response: {e}")
                return FactualAccuracyAnalysis(
                    accuracy_score=0.6,
                    justification="Failed to parse AI response"
                )
                
        except OpenRouterException as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return FactualAccuracyAnalysis(
                accuracy_score=0.6,
                justification=f"AI analysis error: {str(e)}"
            )
    
    def _analyze_bias_and_neutrality(self, content: str) -> BiasAnalysis:
        """
        Analyze bias and neutrality
        
        Args:
            content: Content to analyze
            
        Returns:
            BiasAnalysis
        """
        logger.debug("Analyzing bias and neutrality")
        
        try:
            prompt = f"""Analyze the bias and neutrality of the following content.

Evaluate (0-100 scale where 0 is neutral/good and 100 is biased/bad):
1. Political bias detected
2. Emotional vs neutral language
3. Balance of different perspectives (0=poor balance, 100=excellent balance)
4. Overall objectivity (0=subjective, 100=objective)

Also identify specific bias types if present (e.g., political, cultural, temporal).

Content to analyze (first 2000 chars):
{content[:2000]}

Respond with a JSON object containing:
- political_bias (0-100, where 0 is neutral)
- emotional_language (0-100, where 0 is neutral)
- perspective_balance (0-100, where 100 is well-balanced)
- objectivity_score (0-100, where 100 is most objective)
- detected_biases (array of strings)
- justification (brief explanation)

Calculate neutrality_score (0-1) based on low bias and high objectivity.
"""
            
            response = self.openrouter_client.generate_text(
                prompt=prompt,
                temperature=0.1,
                max_tokens=800
            )
            
            try:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                else:
                    data = json.loads(response)
                
                # Calculate neutrality score (inverse of bias, plus objectivity)
                political_bias = data.get('political_bias', 20)
                emotional = data.get('emotional_language', 20)
                perspective = data.get('perspective_balance', 50)
                objectivity = data.get('objectivity_score', 70)
                
                neutrality_score = (
                    (100 - political_bias) * 0.3 +
                    (100 - emotional) * 0.2 +
                    perspective * 0.2 +
                    objectivity * 0.3
                ) / 100
                
                return BiasAnalysis(
                    neutrality_score=neutrality_score,
                    political_bias=political_bias,
                    emotional_language=emotional,
                    perspective_balance=perspective,
                    objectivity_score=objectivity,
                    detected_biases=data.get('detected_biases', []),
                    justification=data.get('justification', 'AI analysis completed')
                )
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse AI response: {e}")
                return BiasAnalysis(
                    neutrality_score=0.7,
                    justification="Failed to parse AI response"
                )
                
        except OpenRouterException as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return BiasAnalysis(
                neutrality_score=0.7,
                justification=f"AI analysis error: {str(e)}"
            )
    
    def _calculate_information_density(self, content: str, character: str) -> float:
        """
        Calculate information density (words per meaningful fact)
        
        Args:
            content: Content to analyze
            character: Character name
            
        Returns:
            Information density score (lower is better - fewer words per fact)
        """
        logger.debug("Calculating information density")
        
        # Count words
        words = len(content.split())
        
        # Heuristic: count potential facts (sentences with numbers, dates, proper nouns)
        sentences = re.split(r'[.!?]+', content)
        
        fact_indicators = 0
        for sentence in sentences:
            # Numbers (potential dates, ages, quantities)
            if re.search(r'\b\d{1,4}\b', sentence):
                fact_indicators += 1
            # Proper nouns (capitalized words mid-sentence)
            if re.search(r'\s[A-Z][a-z]+', sentence):
                fact_indicators += 1
            # Specific terms
            if re.search(r'\b(born|died|studied|worked|published|discovered|invented)\b', sentence, re.IGNORECASE):
                fact_indicators += 1
        
        # Avoid division by zero
        if fact_indicators == 0:
            fact_indicators = 1
        
        # Information density: words per fact indicator
        # Good biographical content should have high fact density (low score)
        density = words / fact_indicators
        
        logger.debug(f"Information density: {density:.2f} words per fact")
        return density
    
    def _calculate_uniqueness_score(self, content: str, character: str) -> float:
        """
        Calculate content uniqueness score
        
        Args:
            content: Content to analyze
            character: Character name
            
        Returns:
            Uniqueness score (0-1)
        """
        logger.debug("Calculating content uniqueness")
        
        # Heuristic uniqueness indicators
        uniqueness_score = 0.5  # Default
        
        # Check for quotes (indicates primary sources or unique insights)
        quote_count = content.count('"') + content.count('"') + content.count('"')
        if quote_count > 4:
            uniqueness_score += 0.1
        
        # Check for specific dates (indicates detailed research)
        date_patterns = re.findall(r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', content, re.IGNORECASE)
        if len(date_patterns) > 2:
            uniqueness_score += 0.1
        
        # Check for citations/references
        if re.search(r'\[?\d+\]?|\(\d{4}\)', content):
            uniqueness_score += 0.1
        
        # Check for less common words (academic vocabulary)
        uncommon_indicators = ['furthermore', 'nevertheless', 'subsequently', 'consequently', 'thereby']
        for word in uncommon_indicators:
            if word in content.lower():
                uniqueness_score += 0.02
        
        # Cap at 1.0
        uniqueness_score = min(1.0, uniqueness_score)
        
        logger.debug(f"Content uniqueness: {uniqueness_score:.2f}")
        return uniqueness_score
    
    def _create_default_score(self) -> ContentQualityScore:
        """Create default/fallback quality score"""
        return ContentQualityScore(
            biographical_depth=0.3,
            factual_accuracy=0.3,
            information_density=100.0,  # High density = low quality in this context
            neutrality_score=0.5,
            source_citations=0,
            content_uniqueness=0.3,
            overall_score=0.3
        )


# Alias for backwards compatibility with documentation
AdvancedContentAnalyzer = ContentAnalyzer
