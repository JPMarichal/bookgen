"""
Factual Consistency Checker
AI-powered fact extraction and consistency verification
"""
import logging
import re
import json
from typing import List, Dict, Any, Optional

from ..services.openrouter_client import OpenRouterClient, OpenRouterException
from ..api.models.cross_validation import KeyFact

logger = logging.getLogger(__name__)


class FactualConsistencyChecker:
    """Checker for factual consistency using AI"""
    
    def __init__(self, openrouter_client: Optional[OpenRouterClient] = None):
        """
        Initialize fact checker
        
        Args:
            openrouter_client: Optional OpenRouter client instance
        """
        self.openrouter_client = openrouter_client or OpenRouterClient()
        logger.info("FactualConsistencyChecker initialized")
    
    def extract_key_facts(
        self,
        content: str,
        character: str,
        max_facts: int = 10
    ) -> List[KeyFact]:
        """
        Extract key facts from content using AI
        
        Args:
            content: Content to extract facts from
            character: Character name for context
            max_facts: Maximum number of facts to extract
            
        Returns:
            List of KeyFact objects
        """
        logger.debug(f"Extracting key facts about {character}")
        
        if not content or len(content.strip()) < 50:
            logger.warning("Content too short for fact extraction")
            return []
        
        try:
            prompt = f"""Extract {max_facts} key factual statements about {character} from the following content.

Focus on:
- Birth/death dates and places
- Major achievements and events
- Important relationships
- Career milestones
- Historical context

Content (first 2000 chars):
{content[:2000]}

Respond with a JSON array of objects, each containing:
- fact: the factual statement (string)
- confidence: confidence level 0-1 (float)
- category: one of [date, event, relationship, achievement, context] (string)

Example format:
[
  {{"fact": "Born in 1879 in Ulm, Germany", "confidence": 0.95, "category": "date"}},
  {{"fact": "Developed theory of relativity", "confidence": 0.9, "category": "achievement"}}
]
"""
            
            response = self.openrouter_client.generate_text(
                prompt=prompt,
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse JSON response
            try:
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                else:
                    data = json.loads(response)
                
                facts = []
                for idx, item in enumerate(data[:max_facts]):
                    fact = KeyFact(
                        fact=item.get('fact', ''),
                        source_index=0,  # Will be set by caller
                        confidence=float(item.get('confidence', 0.8)),
                        category=item.get('category', 'other')
                    )
                    facts.append(fact)
                
                logger.debug(f"Extracted {len(facts)} facts")
                return facts
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse fact extraction response: {e}")
                return self._fallback_fact_extraction(content, character)
                
        except OpenRouterException as e:
            logger.error(f"OpenRouter error during fact extraction: {e}")
            return self._fallback_fact_extraction(content, character)
        except Exception as e:
            logger.error(f"Unexpected error during fact extraction: {e}")
            return []
    
    def _fallback_fact_extraction(
        self,
        content: str,
        character: str
    ) -> List[KeyFact]:
        """
        Fallback fact extraction using simple heuristics
        
        Args:
            content: Content to extract from
            character: Character name
            
        Returns:
            List of KeyFact objects
        """
        facts = []
        
        # Extract sentences mentioning the character
        sentences = content.split('.')
        for idx, sentence in enumerate(sentences[:20]):
            if character.lower() in sentence.lower() and len(sentence) > 20:
                fact = KeyFact(
                    fact=sentence.strip(),
                    source_index=0,
                    confidence=0.5,
                    category='other'
                )
                facts.append(fact)
                if len(facts) >= 5:
                    break
        
        return facts
    
    def compare_facts(
        self,
        facts1: List[KeyFact],
        facts2: List[KeyFact]
    ) -> float:
        """
        Compare two sets of facts and calculate consistency score
        
        Args:
            facts1: First set of facts
            facts2: Second set of facts
            
        Returns:
            Consistency score (0-1)
        """
        if not facts1 or not facts2:
            return 0.5  # Neutral score if no facts to compare
        
        try:
            # Use AI to compare facts
            facts1_text = "\n".join([f"- {f.fact}" for f in facts1[:10]])
            facts2_text = "\n".join([f"- {f.fact}" for f in facts2[:10]])
            
            prompt = f"""Compare these two sets of facts and determine if they are consistent or contradictory.

Set A:
{facts1_text}

Set B:
{facts2_text}

Respond with a JSON object containing:
- consistency_score: 0-1 (1 = fully consistent, 0 = contradictory)
- contradictions: number of contradictions found (integer)
- agreements: number of agreements found (integer)
- explanation: brief explanation (string)
"""
            
            response = self.openrouter_client.generate_text(
                prompt=prompt,
                temperature=0.1,
                max_tokens=500
            )
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
            else:
                data = json.loads(response)
            
            consistency = float(data.get('consistency_score', 0.7))
            return min(1.0, max(0.0, consistency))
            
        except Exception as e:
            logger.warning(f"Failed to compare facts with AI: {e}")
            return self._fallback_fact_comparison(facts1, facts2)
    
    def _fallback_fact_comparison(
        self,
        facts1: List[KeyFact],
        facts2: List[KeyFact]
    ) -> float:
        """
        Fallback fact comparison using simple text similarity
        
        Args:
            facts1: First set of facts
            facts2: Second set of facts
            
        Returns:
            Consistency score (0-1)
        """
        # Simple overlap check
        text1 = " ".join([f.fact.lower() for f in facts1])
        text2 = " ".join([f.fact.lower() for f in facts2])
        
        # Count common words
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.5
        
        overlap = len(words1.intersection(words2))
        total = len(words1.union(words2))
        
        return overlap / total if total > 0 else 0.5
