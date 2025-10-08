"""
Automatic source generator service using AI and multiple strategies
"""
import logging
import json
from typing import List, Dict, Any
from collections import defaultdict

from ..services.openrouter_client import OpenRouterClient, OpenRouterException
from ..services.source_validator import SourceValidationService
from ..api.models.sources import SourceItem
from ..api.models.source_generation import (
    CharacterAnalysis,
    AutomaticSourceGenerationRequest
)
from ..strategies.source_strategy import SourceStrategy
from ..strategies.wikipedia_strategy import WikipediaStrategy

logger = logging.getLogger(__name__)


class AutomaticSourceGenerator:
    """
    Automatic source generator using AI analysis and multiple search strategies
    
    This service implements the original functionality from .windsurf rules:
    - Automatically generates 40-60 high-quality sources
    - Uses AI to analyze the character and context
    - Applies multiple search strategies
    - Validates sources for quality and relevance
    """
    
    def __init__(
        self,
        openrouter_client: OpenRouterClient = None,
        source_validator: SourceValidationService = None
    ):
        """
        Initialize the automatic source generator
        
        Args:
            openrouter_client: OpenRouter client for AI analysis (creates default if None)
            source_validator: Source validation service (creates default if None)
        """
        self.openrouter_client = openrouter_client or OpenRouterClient()
        self.source_validator = source_validator or SourceValidationService()
        
        # Initialize search strategies
        self.search_strategies: List[SourceStrategy] = [
            WikipediaStrategy(),
            # Future strategies will be added here:
            # AcademicDatabaseStrategy(),
            # GovernmentArchiveStrategy(),
            # BiographyWebsiteStrategy(),
        ]
        
        logger.info(
            f"AutomaticSourceGenerator initialized with {len(self.search_strategies)} strategies"
        )
    
    def generate_sources_for_character(
        self,
        request: AutomaticSourceGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate sources automatically for a character
        
        Args:
            request: Request with character name and generation parameters
            
        Returns:
            Dictionary with generated sources and metadata
        """
        character_name = request.character_name
        logger.info(f"Starting automatic source generation for: {character_name}")
        
        try:
            # Step 1: Analyze character with AI
            character_analysis = self._analyze_character_with_ai(character_name)
            logger.info(f"Character analysis complete for {character_name}")
            
            # Step 2: Generate sources using all strategies
            candidate_sources = self._generate_sources_from_strategies(
                character_name,
                character_analysis
            )
            logger.info(f"Generated {len(candidate_sources)} candidate sources")
            
            # Step 3: Validate and filter sources
            validated_result = self._validate_and_filter_sources(
                candidate_sources,
                character_name,
                request
            )
            logger.info(
                f"Validation complete: {validated_result['valid_count']} valid sources"
            )
            
            # Step 4: Ensure we have enough sources
            final_sources = self._ensure_minimum_sources(
                validated_result['sources'],
                request.min_sources
            )
            logger.info(f"Final source count: {len(final_sources)}")
            
            # Step 5: Build response
            return {
                'character_name': character_name,
                'sources': final_sources,
                'character_analysis': character_analysis,
                'validation_summary': validated_result['validation_summary'],
                'strategies_used': [s.get_strategy_name() for s in self.search_strategies],
                'generation_metadata': {
                    'total_candidates': len(candidate_sources),
                    'valid_sources': validated_result['valid_count'],
                    'final_count': len(final_sources),
                    'meets_minimum': len(final_sources) >= request.min_sources
                }
            }
        
        except Exception as e:
            logger.error(f"Error generating sources: {e}")
            raise
    
    def _analyze_character_with_ai(self, character_name: str) -> CharacterAnalysis:
        """
        Use AI to analyze the character and extract relevant information
        
        Args:
            character_name: Name of the character to analyze
            
        Returns:
            CharacterAnalysis with extracted information
        """
        prompt = f"""Analyze the historical figure "{character_name}" and provide structured information for research purposes.

Provide a JSON response with the following fields:
1. historical_period: The century/era and key years (e.g., "20th century, 1879-1955")
2. nationality: Primary nationality and relevant countries/places
3. professional_field: Main field of work (e.g., "Physics", "Politics", "Literature")
4. key_events: List of 3-5 most important events or achievements
5. related_entities: List of 3-5 related people, concepts, or organizations
6. search_terms: List of 5-8 optimal search terms in English for finding biographical sources

Focus on factual, verifiable information. Format as valid JSON.

Example format:
{{
  "historical_period": "20th century, 1879-1955",
  "nationality": "German-American",
  "professional_field": "Theoretical Physics",
  "key_events": ["Theory of Relativity", "Nobel Prize 1921", "Manhattan Project consultation"],
  "related_entities": ["Niels Bohr", "Quantum Mechanics", "Princeton University"],
  "search_terms": ["Einstein biography", "relativity theory", "Nobel Prize physics", "Princeton", "patent office"]
}}
"""
        
        system_prompt = "You are a historical research assistant. Provide accurate, structured information about historical figures in JSON format."
        
        try:
            # Generate analysis with AI
            response = self.openrouter_client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Low temperature for factual information
                max_tokens=1000
            )
            
            # Parse JSON response
            # Extract JSON from markdown code blocks if present
            response_clean = response.strip()
            if '```json' in response_clean:
                response_clean = response_clean.split('```json')[1].split('```')[0].strip()
            elif '```' in response_clean:
                response_clean = response_clean.split('```')[1].split('```')[0].strip()
            
            analysis_data = json.loads(response_clean)
            
            # Create CharacterAnalysis object
            return CharacterAnalysis(
                character_name=character_name,
                historical_period=analysis_data.get('historical_period'),
                nationality=analysis_data.get('nationality'),
                professional_field=analysis_data.get('professional_field'),
                key_events=analysis_data.get('key_events', []),
                related_entities=analysis_data.get('related_entities', []),
                search_terms=analysis_data.get('search_terms', []),
                metadata={'raw_response': response}
            )
        
        except OpenRouterException as e:
            logger.error(f"OpenRouter error analyzing character: {e}")
            # Return minimal analysis as fallback
            return self._create_fallback_analysis(character_name)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response as JSON: {e}")
            return self._create_fallback_analysis(character_name)
        except Exception as e:
            logger.error(f"Unexpected error in character analysis: {e}")
            return self._create_fallback_analysis(character_name)
    
    def _create_fallback_analysis(self, character_name: str) -> CharacterAnalysis:
        """
        Create a minimal fallback analysis when AI fails
        
        Args:
            character_name: Name of the character
            
        Returns:
            Basic CharacterAnalysis
        """
        return CharacterAnalysis(
            character_name=character_name,
            search_terms=[
                f"{character_name} biography",
                f"{character_name} life",
                f"{character_name} history"
            ]
        )
    
    def _generate_sources_from_strategies(
        self,
        character_name: str,
        character_analysis: CharacterAnalysis
    ) -> List[SourceItem]:
        """
        Generate sources using all available strategies
        
        Args:
            character_name: Name of the character
            character_analysis: AI analysis of the character
            
        Returns:
            Combined list of sources from all strategies
        """
        all_sources = []
        
        for strategy in self.search_strategies:
            try:
                logger.info(f"Running {strategy.get_strategy_name()}...")
                sources = strategy.search(character_name, character_analysis)
                all_sources.extend(sources)
                logger.info(f"{strategy.get_strategy_name()} found {len(sources)} sources")
            except Exception as e:
                logger.error(f"Error in {strategy.get_strategy_name()}: {e}")
                continue
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_sources = []
        for source in all_sources:
            if source.url and source.url in seen_urls:
                continue
            if source.url:
                seen_urls.add(source.url)
            unique_sources.append(source)
        
        logger.info(f"Total unique sources: {len(unique_sources)}")
        return unique_sources
    
    def _validate_and_filter_sources(
        self,
        sources: List[SourceItem],
        character_name: str,
        request: AutomaticSourceGenerationRequest
    ) -> Dict[str, Any]:
        """
        Validate and filter sources using SourceValidationService
        
        Args:
            sources: List of candidate sources
            character_name: Name of the character
            request: Original request with validation parameters
            
        Returns:
            Dictionary with validated sources and summary
        """
        if not sources:
            return {
                'sources': [],
                'valid_count': 0,
                'validation_summary': {}
            }
        
        # Use existing SourceValidationService
        validation_result = self.source_validator.validate_sources(
            biography_topic=character_name,
            sources_list=sources,
            check_accessibility=request.check_accessibility
        )
        
        # Filter sources based on thresholds
        filtered_sources = []
        for result in validation_result['results']:
            # Include source if:
            # 1. It's valid (basic validation passed)
            # 2. AND either relevance or credibility is acceptable
            if result.is_valid:
                relevance_ok = (
                    result.relevance_score is None or
                    result.relevance_score >= request.min_relevance
                )
                credibility_ok = (
                    result.credibility_score is None or
                    result.credibility_score >= request.min_credibility
                )
                
                if relevance_ok and credibility_ok:
                    filtered_sources.append(result.source)
        
        return {
            'sources': filtered_sources,
            'valid_count': len(filtered_sources),
            'validation_summary': {
                'total_validated': validation_result['total_sources'],
                'valid_sources': validation_result['valid_sources'],
                'filtered_count': len(filtered_sources),
                'average_relevance': validation_result.get('average_relevance', 0.0),
                'average_credibility': validation_result.get('average_credibility', 0.0),
                'recommendations': validation_result.get('recommendations', [])
            }
        }
    
    def _ensure_minimum_sources(
        self,
        sources: List[SourceItem],
        min_sources: int
    ) -> List[SourceItem]:
        """
        Ensure we have at least the minimum number of sources
        
        Args:
            sources: List of validated sources
            min_sources: Minimum number required
            
        Returns:
            List of sources (may include warning in metadata)
        """
        if len(sources) < min_sources:
            logger.warning(
                f"Only found {len(sources)} sources, requested minimum was {min_sources}"
            )
        
        return sources
