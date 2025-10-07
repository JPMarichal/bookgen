"""
Text analysis utilities for content quality assessment
"""
import re
from typing import List, Dict, Tuple, Set
from collections import Counter, defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class TextAnalyzer:
    """Utilities for analyzing text content quality"""
    
    def __init__(self):
        """Initialize text analyzer"""
        self.stop_words = 'english'
    
    def count_words(self, text: str) -> int:
        """
        Count words in text
        
        Args:
            text: Text to analyze
            
        Returns:
            Number of words
        """
        # Remove markdown headers, links, and other formatting
        clean_text = self._clean_markdown(text)
        # Split by whitespace and count non-empty tokens
        words = clean_text.split()
        return len(words)
    
    def _clean_markdown(self, text: str) -> str:
        """
        Remove markdown formatting from text
        
        Args:
            text: Text with markdown formatting
            
        Returns:
            Clean text without markdown
        """
        # Remove markdown headers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        # Remove markdown links [text](url)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Remove markdown bold/italic
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        # Remove code blocks
        text = re.sub(r'```[^`]*```', '', text)
        text = re.sub(r'`[^`]+`', '', text)
        return text
    
    def calculate_information_density(self, text: str) -> float:
        """
        Calculate information density using TF-IDF
        
        Args:
            text: Text to analyze
            
        Returns:
            Information density score (0-1)
        """
        try:
            # Clean text
            clean_text = self._clean_markdown(text)
            
            # Need at least some content
            if len(clean_text.strip()) < 100:
                return 0.0
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                stop_words=self.stop_words,
                max_features=500,
                lowercase=True,
                strip_accents='unicode'
            )
            
            # Transform text - use list to handle single document
            tfidf_matrix = vectorizer.fit_transform([clean_text])
            
            # Calculate mean TF-IDF score
            # Higher scores indicate more informative content
            mean_tfidf = np.mean(tfidf_matrix.toarray())
            
            return float(mean_tfidf)
            
        except Exception as e:
            # Return low score on error
            return 0.0
    
    def detect_repetitive_content(
        self,
        text: str,
        ngram_min: int = 3,
        ngram_max: int = 7,
        min_occurrences: int = 3
    ) -> Dict[str, any]:
        """
        Detect repetitive content using n-grams
        
        Args:
            text: Text to analyze
            ngram_min: Minimum n-gram size
            ngram_max: Maximum n-gram size
            min_occurrences: Minimum occurrences to consider as repetitive
            
        Returns:
            Dictionary with repetition analysis
        """
        clean_text = self._clean_markdown(text)
        words = clean_text.lower().split()
        
        if len(words) < ngram_min:
            return {
                'repetition_ratio': 0.0,
                'repetitive_ngrams': [],
                'total_repetitions': 0
            }
        
        # Find repetitive n-grams
        repetitive_ngrams = []
        total_repetitive_words = 0
        
        for n in range(ngram_min, min(ngram_max + 1, len(words))):
            ngrams = self._extract_ngrams(words, n)
            
            # Count n-gram occurrences
            ngram_counts = Counter(ngrams)
            
            # Find repetitive n-grams
            for ngram, count in ngram_counts.items():
                if count >= min_occurrences:
                    repetitive_ngrams.append({
                        'ngram': ' '.join(ngram),
                        'size': n,
                        'occurrences': count
                    })
                    # Count words involved in repetition
                    # (count - 1) because first occurrence is not repetition
                    total_repetitive_words += n * (count - 1)
        
        # Calculate repetition ratio
        repetition_ratio = total_repetitive_words / len(words) if words else 0.0
        
        # Sort by occurrences (most repetitive first)
        repetitive_ngrams.sort(key=lambda x: x['occurrences'], reverse=True)
        
        return {
            'repetition_ratio': repetition_ratio,
            'repetitive_ngrams': repetitive_ngrams[:10],  # Top 10 most repetitive
            'total_repetitions': len(repetitive_ngrams)
        }
    
    def _extract_ngrams(self, words: List[str], n: int) -> List[Tuple[str, ...]]:
        """
        Extract n-grams from word list
        
        Args:
            words: List of words
            n: N-gram size
            
        Returns:
            List of n-grams as tuples
        """
        return [tuple(words[i:i+n]) for i in range(len(words) - n + 1)]
    
    def calculate_vocabulary_richness(self, text: str) -> float:
        """
        Calculate vocabulary richness (unique words ratio)
        
        Args:
            text: Text to analyze
            
        Returns:
            Vocabulary richness score (0-1)
        """
        clean_text = self._clean_markdown(text)
        words = clean_text.lower().split()
        
        if not words:
            return 0.0
        
        unique_words = set(words)
        richness = len(unique_words) / len(words)
        
        return richness
    
    def analyze_sentence_structure(self, text: str) -> Dict[str, any]:
        """
        Analyze sentence structure and complexity
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentence analysis
        """
        clean_text = self._clean_markdown(text)
        
        # Split into sentences (simple approach)
        sentences = re.split(r'[.!?]+', clean_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {
                'sentence_count': 0,
                'avg_sentence_length': 0.0,
                'sentence_variety': 0.0
            }
        
        # Calculate sentence lengths
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_length = np.mean(sentence_lengths) if sentence_lengths else 0
        
        # Calculate sentence variety (standard deviation of lengths)
        # Higher variety indicates more varied sentence structure
        variety = np.std(sentence_lengths) / avg_length if avg_length > 0 else 0
        
        return {
            'sentence_count': len(sentences),
            'avg_sentence_length': float(avg_length),
            'sentence_variety': float(variety)
        }
    
    def extract_key_terms(self, text: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Extract key terms from text using TF-IDF
        
        Args:
            text: Text to analyze
            top_n: Number of top terms to extract
            
        Returns:
            List of (term, score) tuples
        """
        try:
            clean_text = self._clean_markdown(text)
            
            if len(clean_text.strip()) < 50:
                return []
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                stop_words=self.stop_words,
                max_features=100,
                lowercase=True,
                strip_accents='unicode'
            )
            
            # Transform text
            tfidf_matrix = vectorizer.fit_transform([clean_text])
            
            # Get feature names and scores
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Get top N terms
            top_indices = np.argsort(scores)[-top_n:][::-1]
            key_terms = [(feature_names[i], float(scores[i])) for i in top_indices if scores[i] > 0]
            
            return key_terms
            
        except Exception:
            return []
    
    def get_content_statistics(self, text: str) -> Dict[str, any]:
        """
        Get comprehensive content statistics
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with various statistics
        """
        word_count = self.count_words(text)
        clean_text = self._clean_markdown(text)
        
        # Character count (excluding whitespace)
        char_count = len(clean_text.replace(' ', '').replace('\n', ''))
        
        # Paragraph count
        paragraphs = [p.strip() for p in clean_text.split('\n\n') if p.strip()]
        
        # Average word length
        words = clean_text.split()
        avg_word_length = np.mean([len(w) for w in words]) if words else 0
        
        return {
            'word_count': word_count,
            'character_count': char_count,
            'paragraph_count': len(paragraphs),
            'avg_word_length': float(avg_word_length),
            'avg_words_per_paragraph': word_count / len(paragraphs) if paragraphs else 0
        }
