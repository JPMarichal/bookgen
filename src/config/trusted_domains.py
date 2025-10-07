"""
Trusted domains configuration for source credibility checking
"""

# Academic and Educational Institutions
ACADEMIC_DOMAINS = {
    'edu',  # Educational institutions
    'ac.uk',  # UK academic institutions
    'ac.jp',  # Japanese academic institutions
    'edu.au',  # Australian educational institutions
    'edu.cn',  # Chinese educational institutions
}

# Trusted Academic and Research Websites
TRUSTED_ACADEMIC_SITES = {
    # Academic databases and archives
    'jstor.org',
    'scholar.google.com',
    'academia.edu',
    'researchgate.net',
    'arxiv.org',
    'pubmed.ncbi.nlm.nih.gov',
    'sciencedirect.com',
    'springer.com',
    'wiley.com',
    'cambridge.org',
    'oxfordacademic.com',
    
    # Digital libraries and archives
    'archive.org',
    'loc.gov',  # Library of Congress
    'gutenberg.org',
    'hathitrust.org',
    'europeana.eu',
    
    # Historical and biographical resources
    'britannica.com',
    'biography.com',
    'historynet.com',
    'nationalarchives.gov.uk',
    'nara.gov',  # National Archives (US)
    
    # Museums and cultural institutions
    'si.edu',  # Smithsonian
    'metmuseum.org',
    'britishmuseum.org',
    'louvre.fr',
    
    # News and journalism (reputable sources)
    'nytimes.com',
    'washingtonpost.com',
    'theguardian.com',
    'bbc.com',
    'reuters.com',
    'apnews.com',
    'npr.org',
    
    # Wikipedia and Wikimedia
    'wikipedia.org',
    'wikimedia.org',
    'wikidata.org',
}

# Government domains
GOVERNMENT_DOMAINS = {
    'gov',  # US government
    'gov.uk',  # UK government
    'gc.ca',  # Canadian government
    'gov.au',  # Australian government
    'gouv.fr',  # French government
    'gob.es',  # Spanish government
}

# Medium credibility sources (acceptable but not highly trusted)
MEDIUM_CREDIBILITY_SITES = {
    'medium.com',
    'substack.com',
    'blogspot.com',
    'wordpress.com',
    'tumblr.com',
}

# Low credibility indicators (domains to flag)
LOW_CREDIBILITY_INDICATORS = {
    'blogspot',
    'wordpress.com/free',
    'wix.com',
    'weebly.com',
    'freehosting',
}


def get_domain_credibility_score(domain: str) -> float:
    """
    Calculate credibility score for a domain (0-100)
    
    Args:
        domain: Domain name to check
        
    Returns:
        Credibility score from 0-100
    """
    domain_lower = domain.lower()
    
    # Highest credibility: Academic and government domains
    for academic_domain in ACADEMIC_DOMAINS:
        if domain_lower.endswith(f'.{academic_domain}') or domain_lower == academic_domain:
            return 95.0
    
    for gov_domain in GOVERNMENT_DOMAINS:
        if domain_lower.endswith(f'.{gov_domain}') or domain_lower == gov_domain:
            return 95.0
    
    # High credibility: Trusted academic and research sites
    for trusted_site in TRUSTED_ACADEMIC_SITES:
        if trusted_site in domain_lower:
            return 90.0
    
    # Medium credibility
    for medium_site in MEDIUM_CREDIBILITY_SITES:
        if medium_site in domain_lower:
            return 60.0
    
    # Low credibility indicators
    for low_indicator in LOW_CREDIBILITY_INDICATORS:
        if low_indicator in domain_lower:
            return 30.0
    
    # Default: Unknown source - neutral score
    return 50.0


def is_trusted_domain(domain: str) -> bool:
    """
    Check if a domain is in the trusted list
    
    Args:
        domain: Domain name to check
        
    Returns:
        True if domain is trusted
    """
    return get_domain_credibility_score(domain) >= 80.0


def get_domain_category(domain: str) -> str:
    """
    Get the category of a domain
    
    Args:
        domain: Domain name to check
        
    Returns:
        Category name
    """
    domain_lower = domain.lower()
    
    # Check academic domains
    for academic_domain in ACADEMIC_DOMAINS:
        if domain_lower.endswith(f'.{academic_domain}') or domain_lower == academic_domain:
            return "academic"
    
    # Check government domains
    for gov_domain in GOVERNMENT_DOMAINS:
        if domain_lower.endswith(f'.{gov_domain}') or domain_lower == gov_domain:
            return "government"
    
    # Check trusted sites
    for trusted_site in TRUSTED_ACADEMIC_SITES:
        if trusted_site in domain_lower:
            if any(news in trusted_site for news in ['nytimes', 'washington', 'guardian', 'bbc', 'reuters', 'apnews', 'npr']):
                return "news"
            elif any(archive in trusted_site for archive in ['archive', 'loc.gov', 'gutenberg', 'hathitrust', 'europeana']):
                return "archive"
            elif any(museum in trusted_site for museum in ['si.edu', 'museum', 'louvre']):
                return "museum"
            else:
                return "academic"
    
    # Check medium credibility
    for medium_site in MEDIUM_CREDIBILITY_SITES:
        if medium_site in domain_lower:
            return "blog"
    
    # Default
    return "other"
