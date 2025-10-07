"""
Tests for OpenRouter API Client
Unit tests for the OpenRouter client with mocking
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import time
from datetime import datetime

from src.config.openrouter_config import OpenRouterConfig
from src.services.openrouter_client import (
    OpenRouterClient,
    OpenRouterException,
    RateLimitException,
    APIException
)
from src.utils.retry_handler import RetryHandler, RetryException


class TestOpenRouterConfig:
    """Tests for OpenRouter configuration"""
    
    def test_config_from_env(self):
        """Test configuration from environment variables"""
        with patch.dict('os.environ', {
            'OPENROUTER_API_KEY': 'test-key',
            'OPENROUTER_BASE_URL': 'https://test.api.com',
            'OPENROUTER_MODEL': 'test-model'
        }):
            config = OpenRouterConfig()
            assert config.api_key == 'test-key'
            assert config.base_url == 'https://test.api.com'
            assert config.model == 'test-model'
    
    def test_config_validation(self):
        """Test configuration validation"""
        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'}):
            config = OpenRouterConfig()
            assert config.validate() is True
    
    def test_config_missing_api_key(self):
        """Test that missing API key raises error"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="API key is required"):
                OpenRouterConfig()
    
    def test_config_headers(self):
        """Test header generation"""
        with patch.dict('os.environ', {
            'OPENROUTER_API_KEY': 'test-key',
            'SITE_URL': 'https://test.com',
            'SITE_TITLE': 'Test Site'
        }):
            config = OpenRouterConfig()
            headers = config.get_headers()
            assert headers['Authorization'] == 'Bearer test-key'
            assert headers['Content-Type'] == 'application/json'
            assert headers['HTTP-Referer'] == 'https://test.com'
            assert headers['X-Title'] == 'Test Site'


class TestRetryHandler:
    """Tests for retry handler"""
    
    def test_retry_success_first_attempt(self):
        """Test successful execution on first attempt"""
        handler = RetryHandler(max_retries=3)
        mock_func = Mock(return_value="success")
        
        result = handler.execute(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_retry_success_after_failures(self):
        """Test successful execution after retries"""
        handler = RetryHandler(max_retries=3, base_delay=0.01)
        mock_func = Mock(side_effect=[Exception("fail"), Exception("fail"), "success"])
        
        result = handler.execute(mock_func, retry_on=(Exception,))
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_retry_exhausted(self):
        """Test retry exhaustion"""
        handler = RetryHandler(max_retries=2, base_delay=0.01)
        mock_func = Mock(side_effect=Exception("fail"))
        
        with pytest.raises(RetryException):
            handler.execute(mock_func, retry_on=(Exception,))
        
        assert mock_func.call_count == 3  # Initial + 2 retries
    
    def test_retry_delay_calculation(self):
        """Test exponential backoff delay calculation"""
        handler = RetryHandler(base_delay=1.0, exponential_base=2.0, jitter=False)
        
        assert handler.calculate_delay(0) == 1.0
        assert handler.calculate_delay(1) == 2.0
        assert handler.calculate_delay(2) == 4.0


class TestOpenRouterClient:
    """Tests for OpenRouter client"""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration"""
        with patch.dict('os.environ', {
            'OPENROUTER_API_KEY': 'test-key',
            'OPENROUTER_BASE_URL': 'https://api.test.com',
            'OPENROUTER_MODEL': 'test-model'
        }):
            return OpenRouterConfig()
    
    @pytest.fixture
    def client(self, mock_config):
        """Create client instance"""
        return OpenRouterClient(config=mock_config)
    
    def test_client_initialization(self, client):
        """Test client initialization"""
        assert client.config is not None
        assert client._stats['requests'] == 0
        assert client._stats['successful_requests'] == 0
    
    def test_get_usage_stats(self, client):
        """Test usage statistics retrieval"""
        stats = client.get_usage_stats()
        
        assert 'requests' in stats
        assert 'successful_requests' in stats
        assert 'failed_requests' in stats
        assert 'total_tokens' in stats
        assert 'success_rate' in stats
        assert stats['success_rate'] == 0.0  # No requests yet
    
    def test_reset_stats(self, client):
        """Test statistics reset"""
        client._stats['requests'] = 10
        client._stats['successful_requests'] = 8
        
        client.reset_stats()
        
        assert client._stats['requests'] == 0
        assert client._stats['successful_requests'] == 0
    
    @patch('requests.post')
    def test_generate_text_success(self, mock_post, client):
        """Test successful text generation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [
                {'message': {'content': 'Generated text'}}
            ],
            'usage': {
                'total_tokens': 100,
                'prompt_tokens': 20,
                'completion_tokens': 80
            }
        }
        mock_post.return_value = mock_response
        
        result = client.generate_text("Test prompt")
        
        assert result == 'Generated text'
        assert client._stats['requests'] == 1
        assert client._stats['successful_requests'] == 1
        assert client._stats['total_tokens'] == 100
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_generate_text_with_system_prompt(self, mock_post, client):
        """Test text generation with system prompt"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [
                {'message': {'content': 'Generated text'}}
            ],
            'usage': {'total_tokens': 100}
        }
        mock_post.return_value = mock_response
        
        result = client.generate_text(
            "User prompt",
            system_prompt="System instructions"
        )
        
        assert result == 'Generated text'
        
        # Verify the request payload includes both prompts
        call_args = mock_post.call_args
        payload = call_args.kwargs['json']
        assert len(payload['messages']) == 2
        assert payload['messages'][0]['role'] == 'system'
        assert payload['messages'][1]['role'] == 'user'
    
    @patch('requests.post')
    def test_generate_text_rate_limit(self, mock_post, client):
        """Test rate limit handling"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = Exception("Rate limit")
        mock_post.return_value = mock_response
        
        with pytest.raises(OpenRouterException):
            client.generate_text("Test prompt")
        
        assert client._stats['failed_requests'] > 0
    
    @patch('requests.post')
    def test_generate_text_timeout(self, mock_post, client):
        """Test timeout handling"""
        from requests.exceptions import Timeout
        mock_post.side_effect = Timeout("Request timeout")
        
        with pytest.raises(OpenRouterException):
            client.generate_text("Test prompt")
    
    @patch('requests.post')
    def test_rate_limiting_delay(self, mock_post, client):
        """Test that rate limiting introduces delay between requests"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test'}}],
            'usage': {'total_tokens': 10}
        }
        mock_post.return_value = mock_response
        
        # Set a short interval for testing
        client._min_request_interval = 0.1
        
        start = time.time()
        client.generate_text("Test 1")
        client.generate_text("Test 2")
        elapsed = time.time() - start
        
        # Should take at least the minimum interval
        assert elapsed >= 0.1
    
    @patch('requests.post')
    def test_custom_parameters(self, mock_post, client):
        """Test custom generation parameters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test'}}],
            'usage': {'total_tokens': 10}
        }
        mock_post.return_value = mock_response
        
        client.generate_text(
            "Test prompt",
            temperature=0.5,
            max_tokens=1000,
            top_p=0.95
        )
        
        # Verify custom parameters are used
        call_args = mock_post.call_args
        payload = call_args.kwargs['json']
        assert payload['temperature'] == 0.5
        assert payload['max_tokens'] == 1000
        assert payload['top_p'] == 0.95


class TestIntegration:
    """Integration tests (would need actual API key to run)"""
    
    @pytest.mark.skip(reason="Requires actual API key")
    def test_real_api_call(self):
        """Test actual API call (skip in CI)"""
        client = OpenRouterClient()
        response = client.generate_text("Say hello in one word")
        assert len(response) > 0
        
        stats = client.get_usage_stats()
        assert stats['requests'] > 0
        assert stats['successful_requests'] > 0
