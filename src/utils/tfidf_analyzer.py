"""
TF-IDF analyzer for content relevance scoring
"""
import re
from typing import List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class TfidfAnalyzer:
    """Analyzer for calculating content relevance using TF-IDF"""
    
    def __init__(self, max_features: int = 1000, stop_words: str = 'english'):
        """
        Initialize TF-IDF analyzer
        
        Args:
            max_features: Maximum number of features for TF-IDF
            stop_words: Language for stop words filtering
        """
        self.max_features = max_features
        self.stop_words = stop_words
        self.vectorizer = None
    
    def calculate_similarity(
        self,
        reference_text: str,
        content_text: str,
        max_content_length: int = 5000
    ) -> float:
        """
        Calculate TF-IDF similarity between reference and content
        
        Args:
            reference_text: Reference text (e.g., character name + context)
            content_text: Content to analyze
            max_content_length: Maximum length of content to analyze
            
        Returns:
            Similarity score (0-1)
        """
        try:
            # Truncate content if too long
            if len(content_text) > max_content_length:
                content_text = content_text[:max_content_length]
            
            # Create vectorizer
            self.vectorizer = TfidfVectorizer(
                stop_words=self.stop_words,
                max_features=self.max_features,
                lowercase=True,
                strip_accents='unicode'
            )
            
            # Fit and transform both texts
            tfidf_matrix = self.vectorizer.fit_transform([reference_text, content_text])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            # Return low score on error
            return 0.0
    
    def calculate_relevance_with_mentions(
        self,
        character_name: str,
        source_title: str,
        content: str,
        max_content_length: int = 5000
    ) -> float:
        """
        Calculate relevance score with bonus for character mentions
        
        Args:
            character_name: Name of the character/subject
            source_title: Title of the source
            content: Content to analyze
            max_content_length: Maximum content length
            
        Returns:
            Relevance score (0-1)
        """
        # Create reference text with context
        reference_text = f"{character_name} {source_title} biography historical"
        
        # Calculate base TF-IDF similarity
        similarity = self.calculate_similarity(reference_text, content, max_content_length)
        
        # Count direct mentions of character name
        character_mentions = self._count_character_mentions(content, character_name)
        
        # Add bonus for mentions (max 0.3 bonus)
        mention_bonus = min(character_mentions * 0.1, 0.3)
        
        # Return combined score (capped at 1.0)
        return min(similarity + mention_bonus, 1.0)
    
    def _count_character_mentions(self, content: str, character_name: str) -> int:
        """
        Count mentions of character name in content
        
        Args:
            content: Content to search
            character_name: Name to search for
            
        Returns:
            Number of mentions
        """
        try:
            # Use word boundary to avoid partial matches
            pattern = r'\b' + re.escape(character_name) + r'\b'
            matches = re.findall(pattern, content, re.IGNORECASE)
            return len(matches)
        except Exception:
            return 0
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[tuple]:
        """
        Extract top keywords from text using TF-IDF
        
        Args:
            text: Text to analyze
            top_n: Number of top keywords to return
            
        Returns:
            List of (keyword, score) tuples
        """
        try:
            # Create vectorizer if not exists
            if self.vectorizer is None:
                self.vectorizer = TfidfVectorizer(
                    stop_words=self.stop_words,
                    max_features=self.max_features
                )
            
            # Fit and transform
            tfidf_matrix = self.vectorizer.fit_transform([text])
            
            # Get feature names and scores
            feature_names = self.vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Get top N keywords
            top_indices = np.argsort(scores)[-top_n:][::-1]
            keywords = [(feature_names[i], scores[i]) for i in top_indices if scores[i] > 0]
            
            return keywords
            
        except Exception:
            return []
    
    def simple_relevance_score(self, content: str, character_name: str) -> float:
        """
        Fallback simple relevance scoring based on term frequency
        
        Args:
            content: Content to analyze
            character_name: Character name to search for
            
        Returns:
            Simple relevance score (0-1)
        """
        content_lower = content.lower()
        character_lower = character_name.lower()
        
        # Count character name mentions
        name_count = content_lower.count(character_lower)
        
        # Count related biographical terms
        biographical_terms = [
            'biography', 'life', 'born', 'died', 'career', 'work', 
            'achievement', 'contribution', 'legacy', 'history'
        ]
        bio_term_count = sum(content_lower.count(term) for term in biographical_terms)
        
        # Calculate simple score
        # More mentions = higher score, but with diminishing returns
        name_score = min(name_count * 0.1, 0.5)
        bio_score = min(bio_term_count * 0.02, 0.3)
        
        return min(name_score + bio_score, 1.0)
