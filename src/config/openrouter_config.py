"""
OpenRouter API Configuration
Configuration class for OpenRouter API client
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class OpenRouterConfig:
    """Configuration for OpenRouter API client"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        site_url: Optional[str] = None,
        site_title: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        timeout: Optional[int] = None
    ):
        """
        Initialize OpenRouter configuration
        
        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
            base_url: Base URL for OpenRouter API (defaults to OPENROUTER_BASE_URL env var)
            model: Model to use (defaults to OPENROUTER_MODEL env var)
            site_url: Site URL for OpenRouter rankings (defaults to SITE_URL env var)
            site_title: Site title for OpenRouter rankings (defaults to SITE_TITLE env var)
            max_tokens: Maximum tokens per request (default: 8192)
            temperature: Temperature for generation (default: 0.7)
            top_p: Top-p for diversity (default: 0.9)
            timeout: Request timeout in seconds (default: 300)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = (base_url or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")).rstrip("/")
        self.model = model or os.getenv("OPENROUTER_MODEL", "qwen/qwen2.5-vl-72b-instruct:free")
        self.site_url = site_url or os.getenv("SITE_URL", "https://bookgen.ai")
        self.site_title = site_title or os.getenv("SITE_TITLE", "BookGen AI System")
        self.max_tokens = max_tokens or int(os.getenv("OPENROUTER_MAX_TOKENS", "8192"))
        self.temperature = temperature if temperature is not None else float(os.getenv("OPENROUTER_TEMPERATURE", "0.7"))
        self.top_p = top_p if top_p is not None else float(os.getenv("OPENROUTER_TOP_P", "0.9"))
        self.timeout = timeout or int(os.getenv("OPENROUTER_TIMEOUT", "300"))
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")
    
    def get_headers(self) -> dict:
        """Get headers for OpenRouter API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_title,
        }
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.api_key:
            raise ValueError("API key is required")
        if not self.base_url:
            raise ValueError("Base URL is required")
        if not self.model:
            raise ValueError("Model is required")
        if self.max_tokens <= 0:
            raise ValueError("Max tokens must be positive")
        if not 0 <= self.temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        if not 0 <= self.top_p <= 1:
            raise ValueError("Top-p must be between 0 and 1")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        return True
