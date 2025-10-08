"""
Premium Domain Registry - Curated database of high-quality domains
"""
from typing import Dict, List, Optional


class PremiumDomainRegistry:
    """Curated database of maximum quality domains"""
    
    # Tier 1 Academic Institutions and Databases
    TIER_1_ACADEMIC = {
        # Top-tier academic institutions
        'harvard.edu': {
            'authority': 98,
            'specialty': ['biography', 'history', 'science'],
            'editorial_process': 'peer_reviewed'
        },
        'oxford.ac.uk': {
            'authority': 97,
            'specialty': ['history', 'literature', 'philosophy'],
            'editorial_process': 'peer_reviewed'
        },
        'cambridge.org': {
            'authority': 96,
            'specialty': ['academic_publishing', 'research'],
            'editorial_process': 'peer_reviewed'
        },
        'jstor.org': {
            'authority': 95,
            'specialty': ['academic_papers', 'historical_documents'],
            'editorial_process': 'peer_reviewed'
        },
        'archive.org': {
            'authority': 94,
            'specialty': ['historical_documents', 'books', 'primary_sources'],
            'editorial_process': 'curated'
        },
        'stanford.edu': {
            'authority': 98,
            'specialty': ['science', 'technology', 'biography'],
            'editorial_process': 'peer_reviewed'
        },
        'mit.edu': {
            'authority': 98,
            'specialty': ['science', 'technology', 'engineering'],
            'editorial_process': 'peer_reviewed'
        },
        'yale.edu': {
            'authority': 97,
            'specialty': ['history', 'law', 'arts'],
            'editorial_process': 'peer_reviewed'
        },
        'princeton.edu': {
            'authority': 97,
            'specialty': ['science', 'mathematics', 'history'],
            'editorial_process': 'peer_reviewed'
        },
    }
    
    # Government Archives and National Libraries
    GOVERNMENT_ARCHIVES = {
        # National libraries and archives
        'loc.gov': {
            'authority': 98,
            'specialty': ['us_history', 'documents', 'manuscripts'],
            'editorial_process': 'government_curated'
        },
        'bl.uk': {
            'authority': 96,
            'specialty': ['british_history', 'manuscripts', 'rare_books'],
            'editorial_process': 'government_curated'
        },
        'bnf.fr': {
            'authority': 95,
            'specialty': ['french_history', 'literature', 'manuscripts'],
            'editorial_process': 'government_curated'
        },
        'nationalarchives.gov.uk': {
            'authority': 96,
            'specialty': ['british_history', 'government_records'],
            'editorial_process': 'government_curated'
        },
        'nara.gov': {
            'authority': 96,
            'specialty': ['us_history', 'government_records'],
            'editorial_process': 'government_curated'
        },
        
        # International organizations
        'unesco.org': {
            'authority': 93,
            'specialty': ['culture', 'education', 'science'],
            'editorial_process': 'international_organization'
        },
        'un.org': {
            'authority': 92,
            'specialty': ['international_relations', 'peace', 'development'],
            'editorial_process': 'international_organization'
        },
    }
    
    # Encyclopedic and Reference Sources
    TIER_1_ENCYCLOPEDIC = {
        'britannica.com': {
            'authority': 94,
            'specialty': ['general_knowledge', 'biography', 'history'],
            'editorial_process': 'expert_reviewed'
        },
        'oxfordreference.com': {
            'authority': 93,
            'specialty': ['academic_reference', 'biography', 'history'],
            'editorial_process': 'peer_reviewed'
        },
        'encyclopedia.com': {
            'authority': 85,
            'specialty': ['general_knowledge', 'biography'],
            'editorial_process': 'editorial_review'
        },
    }
    
    # Biographical Websites
    TIER_1_BIOGRAPHICAL = {
        'biography.com': {
            'authority': 88,
            'specialty': ['celebrity', 'historical_figures', 'biography'],
            'editorial_process': 'editorial_review'
        },
        'nobelprize.org': {
            'authority': 96,
            'specialty': ['science', 'peace', 'literature', 'economics'],
            'editorial_process': 'official_records'
        },
        'historynet.com': {
            'authority': 82,
            'specialty': ['military_history', 'political_figures'],
            'editorial_process': 'editorial_review'
        },
        'history.com': {
            'authority': 80,
            'specialty': ['history', 'biography', 'historical_events'],
            'editorial_process': 'editorial_review'
        },
    }
    
    # News Archives (Premium)
    TIER_1_NEWS_ARCHIVES = {
        'nytimes.com': {
            'authority': 88,
            'specialty': ['news', 'biography', 'contemporary_history'],
            'editorial_process': 'journalistic_standards'
        },
        'washingtonpost.com': {
            'authority': 86,
            'specialty': ['news', 'politics', 'biography'],
            'editorial_process': 'journalistic_standards'
        },
        'theguardian.com': {
            'authority': 85,
            'specialty': ['news', 'international', 'biography'],
            'editorial_process': 'journalistic_standards'
        },
        'reuters.com': {
            'authority': 87,
            'specialty': ['news', 'international', 'business'],
            'editorial_process': 'journalistic_standards'
        },
        'apnews.com': {
            'authority': 87,
            'specialty': ['news', 'international'],
            'editorial_process': 'journalistic_standards'
        },
        'bbc.com': {
            'authority': 86,
            'specialty': ['news', 'international', 'biography'],
            'editorial_process': 'journalistic_standards'
        },
    }
    
    @classmethod
    def get_domain_info(cls, domain: str) -> Optional[Dict]:
        """
        Get information about a specific domain
        
        Args:
            domain: Domain name to look up
            
        Returns:
            Domain info dict or None if not found
        """
        domain_lower = domain.lower()
        
        # Search in all registries
        for registry in [
            cls.TIER_1_ACADEMIC,
            cls.GOVERNMENT_ARCHIVES,
            cls.TIER_1_ENCYCLOPEDIC,
            cls.TIER_1_BIOGRAPHICAL,
            cls.TIER_1_NEWS_ARCHIVES
        ]:
            # Check exact match
            if domain_lower in registry:
                return registry[domain_lower]
            
            # Check if domain ends with any registered domain
            for registered_domain, info in registry.items():
                if domain_lower.endswith(registered_domain):
                    return info
        
        return None
    
    @classmethod
    def get_authority_score(cls, domain: str) -> float:
        """
        Get authority score for a domain
        
        Args:
            domain: Domain name
            
        Returns:
            Authority score (0-100)
        """
        info = cls.get_domain_info(domain)
        if info:
            return info.get('authority', 50.0)
        return 50.0
    
    @classmethod
    def get_category(cls, domain: str) -> str:
        """
        Get the category of a domain
        
        Args:
            domain: Domain name
            
        Returns:
            Category name
        """
        domain_lower = domain.lower()
        
        if any(domain_lower.endswith(d) or d in domain_lower 
               for d in cls.TIER_1_ACADEMIC.keys()):
            return "academic"
        
        if any(domain_lower.endswith(d) or d in domain_lower 
               for d in cls.GOVERNMENT_ARCHIVES.keys()):
            return "government"
        
        if any(domain_lower.endswith(d) or d in domain_lower 
               for d in cls.TIER_1_ENCYCLOPEDIC.keys()):
            return "encyclopedic"
        
        if any(domain_lower.endswith(d) or d in domain_lower 
               for d in cls.TIER_1_BIOGRAPHICAL.keys()):
            return "biographical"
        
        if any(domain_lower.endswith(d) or d in domain_lower 
               for d in cls.TIER_1_NEWS_ARCHIVES.keys()):
            return "news"
        
        return "other"
    
    @classmethod
    def is_premium_domain(cls, domain: str) -> bool:
        """
        Check if domain is in premium registry
        
        Args:
            domain: Domain name
            
        Returns:
            True if premium domain
        """
        return cls.get_domain_info(domain) is not None
    
    @classmethod
    def get_all_domains_by_category(cls, category: str) -> List[str]:
        """
        Get all domains in a specific category
        
        Args:
            category: Category name (academic, government, etc.)
            
        Returns:
            List of domain names
        """
        category_map = {
            'academic': cls.TIER_1_ACADEMIC,
            'government': cls.GOVERNMENT_ARCHIVES,
            'encyclopedic': cls.TIER_1_ENCYCLOPEDIC,
            'biographical': cls.TIER_1_BIOGRAPHICAL,
            'news': cls.TIER_1_NEWS_ARCHIVES,
        }
        
        registry = category_map.get(category, {})
        return list(registry.keys())
