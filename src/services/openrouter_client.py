"""
OpenRouter API Client
Robust client for OpenRouter API with rate limiting, error handling, and retry logic
"""
import time
import logging
import json
from typing import Optional, Dict, Any, Iterator
from datetime import datetime, timezone

import requests
from requests.exceptions import RequestException, Timeout, HTTPError

from ..config.openrouter_config import OpenRouterConfig
from ..utils.retry_handler import RetryHandler, with_retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenRouterException(Exception):
    """Base exception for OpenRouter client errors"""
    pass


class RateLimitException(OpenRouterException):
    """Exception raised when rate limit is exceeded"""
    pass


class APIException(OpenRouterException):
    """Exception raised for API errors"""
    pass


class OpenRouterClient:
    """
    Client for OpenRouter API with advanced features:
    - Rate limiting
    - Error handling
    - Retry logic with exponential backoff
    - Usage tracking
    - Streaming support
    - Detailed logging
    """
    
    def __init__(self, config: Optional[OpenRouterConfig] = None):
        """
        Initialize OpenRouter client
        
        Args:
            config: OpenRouter configuration (defaults to environment-based config)
        """
        self.config = config or OpenRouterConfig()
        self.config.validate()
        
        self.retry_handler = RetryHandler(
            max_retries=3,
            base_delay=1.0,
            max_delay=60.0,
            exponential_base=2.0
        )
        
        # Usage statistics
        self._stats = {
            "requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_cost": 0.0,
            "errors": [],
            "start_time": datetime.now(timezone.utc)
        }
        
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 1.0  # Minimum 1 second between requests for free tier
        
        logger.info(f"OpenRouter client initialized with model: {self.config.model}")
    
    def _wait_for_rate_limit(self):
        """Wait if needed to respect rate limits"""
        if self._last_request_time > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self._min_request_interval:
                wait_time = self._min_request_interval - elapsed
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
                time.sleep(wait_time)
    
    def _update_stats(self, success: bool, usage: Optional[Dict] = None, error: Optional[str] = None):
        """Update usage statistics"""
        self._stats["requests"] += 1
        
        if success:
            self._stats["successful_requests"] += 1
            if usage:
                self._stats["total_tokens"] += usage.get("total_tokens", 0)
                self._stats["total_prompt_tokens"] += usage.get("prompt_tokens", 0)
                self._stats["total_completion_tokens"] += usage.get("completion_tokens", 0)
        else:
            self._stats["failed_requests"] += 1
            if error:
                self._stats["errors"].append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error": error
                })
    
    def _make_request(
        self,
        messages: list[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Make a request to OpenRouter API
        
        Args:
            messages: List of message dictionaries
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            top_p: Top-p for diversity
            stream: Whether to stream the response
            
        Returns:
            API response
            
        Raises:
            RateLimitException: If rate limit is exceeded
            APIException: If API returns an error
            RequestException: If request fails
        """
        self._wait_for_rate_limit()
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "top_p": top_p or self.config.top_p,
        }
        
        if stream:
            payload["stream"] = True
        
        url = f"{self.config.base_url}/chat/completions"
        headers = self.config.get_headers()
        
        logger.info(f"Making request to {url} with model {self.config.model}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=self.config.timeout,
                stream=stream
            )
            
            self._last_request_time = time.time()
            
            # Check for rate limiting
            if response.status_code == 429:
                error_msg = "Rate limit exceeded"
                logger.error(error_msg)
                self._update_stats(success=False, error=error_msg)
                raise RateLimitException(error_msg)
            
            # Check for other HTTP errors
            response.raise_for_status()
            
            if stream:
                return response
            else:
                result = response.json()
                logger.info(f"Request successful. Status: {response.status_code}")
                logger.debug(f"Response: {json.dumps(result, indent=2)}")
                return result
                
        except Timeout as e:
            error_msg = f"Request timeout after {self.config.timeout}s"
            logger.error(error_msg)
            self._update_stats(success=False, error=error_msg)
            raise APIException(error_msg) from e
        except HTTPError as e:
            error_msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            self._update_stats(success=False, error=error_msg)
            raise APIException(error_msg) from e
        except RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            self._update_stats(success=False, error=error_msg)
            raise APIException(error_msg) from e
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None
    ) -> str:
        """
        Generate text from a prompt
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            top_p: Top-p for diversity
            
        Returns:
            Generated text
            
        Raises:
            OpenRouterException: If generation fails
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        def _generate():
            return self._make_request(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stream=False
            )
        
        try:
            # Use retry handler for the request
            result = self.retry_handler.execute(
                _generate,
                retry_on=(RequestException, APIException, RateLimitException)
            )
            
            # Extract text from response
            content = result["choices"][0]["message"]["content"]
            
            # Update stats with usage info
            usage = result.get("usage", {})
            self._update_stats(success=True, usage=usage)
            
            logger.info(f"Generated {usage.get('completion_tokens', 0)} tokens")
            
            return content
            
        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            raise OpenRouterException(f"Text generation failed: {str(e)}") from e
    
    def generate_text_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None
    ) -> Iterator[str]:
        """
        Generate text with streaming response
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            top_p: Top-p for diversity
            
        Yields:
            Chunks of generated text
            
        Raises:
            OpenRouterException: If generation fails
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self._make_request(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stream=True
            )
            
            logger.info("Starting streaming response")
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse streaming chunk: {data}")
            
            self._update_stats(success=True)
            logger.info("Streaming completed successfully")
            
        except Exception as e:
            logger.error(f"Streaming generation failed: {str(e)}")
            self._update_stats(success=False, error=str(e))
            raise OpenRouterException(f"Streaming generation failed: {str(e)}") from e
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics
        
        Returns:
            Dictionary with usage statistics
        """
        stats = self._stats.copy()
        stats["uptime_seconds"] = (datetime.now(timezone.utc) - stats["start_time"]).total_seconds()
        stats["start_time"] = stats["start_time"].isoformat()
        
        # Calculate success rate
        if stats["requests"] > 0:
            stats["success_rate"] = stats["successful_requests"] / stats["requests"]
        else:
            stats["success_rate"] = 0.0
        
        return stats
    
    def reset_stats(self):
        """Reset usage statistics"""
        self._stats = {
            "requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_cost": 0.0,
            "errors": [],
            "start_time": datetime.now(timezone.utc)
        }
        logger.info("Usage statistics reset")
