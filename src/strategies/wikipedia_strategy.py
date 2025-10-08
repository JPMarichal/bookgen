"""
Wikipedia strategy for source generation
"""
import logging
from typing import List, Optional
import requests
from requests.exceptions import RequestException

from .source_strategy import SourceStrategy
from ..api.models.sources import SourceItem, SourceType
from ..api.models.source_generation import CharacterAnalysis

logger = logging.getLogger(__name__)


class WikipediaStrategy(SourceStrategy):
    """
    Strategy for generating sources from Wikipedia
    
    Searches Wikipedia API for the character and related topics,
    extracting main article, related pages, and external references
    """
    
    def __init__(self):
        """Initialize Wikipedia strategy"""
        super().__init__()
        self.api_base = "https://en.wikipedia.org/w/api.php"
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with proper headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'BookGen/1.0 (Educational Biography Generator)',
            'Accept': 'application/json'
        })
        return session
    
    def search(
        self,
        character_name: str,
        character_analysis: CharacterAnalysis
    ) -> List[SourceItem]:
        """
        Search Wikipedia for sources about the character
        
        Args:
            character_name: Name of the character
            character_analysis: AI analysis with search context
            
        Returns:
            List of SourceItem objects from Wikipedia
        """
        sources = []
        
        try:
            # 1. Search for the main Wikipedia article
            main_article = self._find_main_article(character_name)
            if main_article:
                sources.append(main_article)
                logger.info(f"Found main Wikipedia article for {character_name}")
            
            # 2. Get related articles based on character analysis
            related_articles = self._find_related_articles(
                character_name,
                character_analysis
            )
            sources.extend(related_articles)
            logger.info(f"Found {len(related_articles)} related Wikipedia articles")
            
            # 3. Extract external references from main article
            if main_article:
                external_refs = self._extract_external_references(character_name)
                sources.extend(external_refs)
                logger.info(f"Found {len(external_refs)} external references")
        
        except Exception as e:
            logger.error(f"Error in WikipediaStrategy search: {e}")
        
        return sources
    
    def _find_main_article(self, character_name: str) -> Optional[SourceItem]:
        """
        Find the main Wikipedia article for the character
        
        Args:
            character_name: Name of the character
            
        Returns:
            SourceItem for the main article, or None if not found
        """
        try:
            # Search for the page
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': character_name,
                'srlimit': 1
            }
            
            response = self.session.get(self.api_base, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('query', {}).get('search'):
                logger.warning(f"No Wikipedia article found for {character_name}")
                return None
            
            page_title = data['query']['search'][0]['title']
            
            # Get page info
            page_info = self._get_page_info(page_title)
            if not page_info:
                return None
            
            # Create source item
            return SourceItem(
                url=f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}",
                title=f"Wikipedia: {page_title}",
                author="Wikipedia Contributors",
                publication_date=None,  # Wikipedia is continuously updated
                source_type=SourceType.URL
            )
        
        except RequestException as e:
            logger.error(f"Error finding main Wikipedia article: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error finding main article: {e}")
            return None
    
    def _find_related_articles(
        self,
        character_name: str,
        character_analysis: CharacterAnalysis
    ) -> List[SourceItem]:
        """
        Find related Wikipedia articles based on character analysis
        
        Args:
            character_name: Name of the character
            character_analysis: AI analysis with related entities
            
        Returns:
            List of related Wikipedia articles
        """
        sources = []
        
        # Use search terms from character analysis
        search_terms = character_analysis.search_terms[:5]  # Limit to top 5
        
        for term in search_terms:
            try:
                params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'search',
                    'srsearch': f'{character_name} {term}',
                    'srlimit': 2
                }
                
                response = self.session.get(self.api_base, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                for result in data.get('query', {}).get('search', []):
                    page_title = result['title']
                    
                    # Skip the main article (already added)
                    if page_title.lower() == character_name.lower():
                        continue
                    
                    source = SourceItem(
                        url=f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}",
                        title=f"Wikipedia: {page_title}",
                        author="Wikipedia Contributors",
                        publication_date=None,
                        source_type=SourceType.URL
                    )
                    sources.append(source)
            
            except Exception as e:
                logger.warning(f"Error searching for related term '{term}': {e}")
                continue
        
        return sources
    
    def _extract_external_references(self, character_name: str) -> List[SourceItem]:
        """
        Extract external references from the main Wikipedia article
        
        Args:
            character_name: Name of the character
            
        Returns:
            List of external references as SourceItem objects
        """
        sources = []
        
        try:
            # Get external links from the article
            params = {
                'action': 'query',
                'format': 'json',
                'titles': character_name,
                'prop': 'extlinks',
                'ellimit': 20  # Limit to 20 external links
            }
            
            response = self.session.get(self.api_base, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if page_id == '-1':  # Page not found
                    continue
                
                extlinks = page_data.get('extlinks', [])
                for link in extlinks:
                    url = link.get('*', '')
                    
                    # Filter for quality domains
                    if self._is_quality_external_link(url):
                        # Extract a reasonable title from URL
                        title = self._extract_title_from_url(url)
                        
                        source = SourceItem(
                            url=url,
                            title=title,
                            author=None,
                            publication_date=None,
                            source_type=SourceType.URL
                        )
                        sources.append(source)
        
        except Exception as e:
            logger.warning(f"Error extracting external references: {e}")
        
        return sources
    
    def _get_page_info(self, page_title: str) -> Optional[dict]:
        """
        Get detailed information about a Wikipedia page
        
        Args:
            page_title: Title of the page
            
        Returns:
            Page information dictionary or None
        """
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'titles': page_title,
                'prop': 'info'
            }
            
            response = self.session.get(self.api_base, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_info in pages.items():
                if page_id != '-1':
                    return page_info
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting page info: {e}")
            return None
    
    def _is_quality_external_link(self, url: str) -> bool:
        """
        Check if external link is from a quality source
        
        Args:
            url: URL to check
            
        Returns:
            True if quality source, False otherwise
        """
        quality_domains = [
            'archive.org',
            'britannica.com',
            'biography.com',
            'nobelprize.org',
            'loc.gov',
            'history.com',
            '.edu',
            '.gov',
            'jstor.org',
            'gutenberg.org'
        ]
        
        url_lower = url.lower()
        return any(domain in url_lower for domain in quality_domains)
    
    def _extract_title_from_url(self, url: str) -> str:
        """
        Extract a reasonable title from a URL
        
        Args:
            url: URL to extract title from
            
        Returns:
            Extracted title
        """
        # Remove protocol and www
        title = url.replace('https://', '').replace('http://', '').replace('www.', '')
        
        # Get domain and path
        parts = title.split('/')
        if len(parts) > 1:
            domain = parts[0]
            # Use last meaningful part of path as title
            path_parts = [p for p in parts[1:] if p and p not in ['index.html', 'index.php']]
            if path_parts:
                title = f"{domain}: {path_parts[-1].replace('-', ' ').replace('_', ' ').title()}"
            else:
                title = domain
        else:
            title = parts[0]
        
        return title[:200]  # Limit length
