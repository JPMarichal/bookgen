"""
Text analysis utilities for chapter validation
Provides density analysis, repetition detection, and n-gram analysis
"""
import re
from collections import Counter
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


class TextAnalyzer:
    """Analyzer for text quality metrics"""
    
    def __init__(self, max_features: int = 1000, ngram_size: int = 5):
        """
        Initialize text analyzer
        
        Args:
            max_features: Maximum features for TF-IDF analysis
            ngram_size: Size of n-grams for repetition detection
        """
        self.max_features = max_features
        self.ngram_size = ngram_size
    
    def count_words(self, text: str) -> int:
        """
        Count words in text (same logic as check_lengths.py)
        
        Args:
            text: Text to analyze
            
        Returns:
            Word count
        """
        return len(text.split())
    
    def calculate_information_density(self, text: str) -> float:
        """
        Calculate information density using TF-IDF
        Higher density = more unique, informative content
        
        Args:
            text: Text to analyze
            
        Returns:
            Density score (0-1)
        """
        if not text or len(text.split()) < 10:
            return 0.0
        
        try:
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                stop_words='english',
                lowercase=True,
                strip_accents='unicode'
            )
            
            # Split text into sentences for better analysis
            sentences = self._split_into_sentences(text)
            if len(sentences) < 2:
                sentences = [text]
            
            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform(sentences)
            
            # Calculate mean TF-IDF score across all terms
            # Higher mean = more informative content
            scores = tfidf_matrix.toarray()
            mean_score = np.mean(scores[scores > 0])
            
            # Normalize to 0-1 range (TF-IDF scores are typically 0-1 but can vary)
            return min(float(mean_score), 1.0)
            
        except Exception as e:
            # Fallback: simple uniqueness ratio
            words = text.lower().split()
            if len(words) == 0:
                return 0.0
            unique_ratio = len(set(words)) / len(words)
            return unique_ratio
    
    def detect_repetitive_content(self, text: str) -> Dict[str, float]:
        """
        Detect repetitive content using n-grams
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with repetition metrics
        """
        words = text.lower().split()
        
        if len(words) < self.ngram_size:
            return {
                'repetition_score': 0.0,
                'most_repeated_ngram': '',
                'repetition_count': 0,
                'total_ngrams': 0
            }
        
        # Generate n-grams
        ngrams = []
        for i in range(len(words) - self.ngram_size + 1):
            ngram = ' '.join(words[i:i + self.ngram_size])
            ngrams.append(ngram)
        
        if not ngrams:
            return {
                'repetition_score': 0.0,
                'most_repeated_ngram': '',
                'repetition_count': 0,
                'total_ngrams': 0
            }
        
        # Count n-gram frequencies
        ngram_counts = Counter(ngrams)
        total_ngrams = len(ngrams)
        
        # Find most repeated n-gram
        most_common = ngram_counts.most_common(1)[0] if ngram_counts else ('', 0)
        most_repeated_ngram, repetition_count = most_common
        
        # Calculate repetition score (what % of n-grams are duplicates)
        unique_ngrams = len(set(ngrams))
        repetition_score = 1.0 - (unique_ngrams / total_ngrams) if total_ngrams > 0 else 0.0
        
        return {
            'repetition_score': repetition_score,
            'most_repeated_ngram': most_repeated_ngram,
            'repetition_count': repetition_count,
            'total_ngrams': total_ngrams
        }
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Extract top keywords using TF-IDF
        
        Args:
            text: Text to analyze
            top_n: Number of keywords to extract
            
        Returns:
            List of (keyword, score) tuples
        """
        if not text or len(text.split()) < 5:
            return []
        
        try:
            vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                stop_words='english',
                lowercase=True
            )
            
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Get top N keywords
            top_indices = np.argsort(scores)[-top_n:][::-1]
            keywords = [(feature_names[i], float(scores[i])) for i in top_indices if scores[i] > 0]
            
            return keywords
        except Exception:
            return []
    
    def calculate_readability_metrics(self, text: str) -> Dict[str, float]:
        """
        Calculate basic readability metrics
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with readability metrics
        """
        words = text.split()
        sentences = self._split_into_sentences(text)
        
        if not words or not sentences:
            return {
                'avg_sentence_length': 0.0,
                'avg_word_length': 0.0,
                'sentence_count': 0,
                'word_count': 0
            }
        
        # Average words per sentence
        avg_sentence_length = len(words) / len(sentences)
        
        # Average word length
        total_chars = sum(len(word) for word in words)
        avg_word_length = total_chars / len(words) if words else 0.0
        
        return {
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,
            'sentence_count': len(sentences),
            'word_count': len(words)
        }
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting on common terminators
        # Using regex to split on . ! ? followed by space and capital letter
        sentences = re.split(r'[.!?]+\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def analyze_content_balance(self, text: str) -> Dict[str, any]:
        """
        Analyze if content is balanced (not too much dialogue, description, etc.)
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with balance metrics
        """
        # Count dialogue (text in quotes)
        dialogue_pattern = r'["\']([^"\']+)["\']'
        dialogue_matches = re.findall(dialogue_pattern, text)
        dialogue_words = sum(len(d.split()) for d in dialogue_matches)
        
        total_words = self.count_words(text)
        
        if total_words == 0:
            return {
                'dialogue_ratio': 0.0,
                'narrative_ratio': 1.0,
                'is_balanced': True
            }
        
        dialogue_ratio = dialogue_words / total_words
        narrative_ratio = 1.0 - dialogue_ratio
        
        # Content is balanced if dialogue is between 20-60%
        is_balanced = 0.2 <= dialogue_ratio <= 0.6
        
        return {
            'dialogue_ratio': dialogue_ratio,
            'narrative_ratio': narrative_ratio,
            'is_balanced': is_balanced
        }
