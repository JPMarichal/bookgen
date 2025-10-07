"""
Retry Handler with Exponential Backoff
System for handling retries with exponential backoff for API calls
"""
import time
import logging
from typing import Callable, Any, Optional, Type
from functools import wraps

logger = logging.getLogger(__name__)


class RetryException(Exception):
    """Exception raised when retry attempts are exhausted"""
    pass


class RetryHandler:
    """Handler for retry logic with exponential backoff"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize retry handler
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delay
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given attempt number
        
        Args:
            attempt: Current attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        delay = min(self.base_delay * (self.exponential_base ** attempt), self.max_delay)
        
        if self.jitter:
            import random
            delay = delay * (0.5 + random.random() * 0.5)
        
        return delay
    
    def execute(
        self,
        func: Callable,
        *args,
        retry_on: tuple[Type[Exception], ...] = (Exception,),
        **kwargs
    ) -> Any:
        """
        Execute a function with retry logic
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            retry_on: Tuple of exception types to retry on
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function
            
        Raises:
            RetryException: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except retry_on as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    func_name = getattr(func, '__name__', repr(func))
                    logger.error(
                        f"All {self.max_retries} retry attempts exhausted for {func_name}",
                        exc_info=True
                    )
                    raise RetryException(
                        f"Failed after {self.max_retries + 1} attempts: {str(e)}"
                    ) from e
                
                delay = self.calculate_delay(attempt)
                func_name = getattr(func, '__name__', repr(func))
                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries + 1} failed for {func_name}. "
                    f"Retrying in {delay:.2f}s. Error: {str(e)}"
                )
                time.sleep(delay)
            except Exception as e:
                # Don't retry on unexpected exceptions
                func_name = getattr(func, '__name__', repr(func))
                logger.error(f"Unexpected error in {func_name}: {str(e)}", exc_info=True)
                raise
        
        # Should never reach here
        raise RetryException(f"Unexpected retry loop termination") from last_exception


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retry_on: tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for adding retry logic to functions
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        retry_on: Tuple of exception types to retry on
        
    Example:
        @with_retry(max_retries=3, retry_on=(requests.RequestException,))
        def api_call():
            # Your API call here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            handler = RetryHandler(
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                exponential_base=exponential_base
            )
            return handler.execute(func, *args, retry_on=retry_on, **kwargs)
        return wrapper
    return decorator
