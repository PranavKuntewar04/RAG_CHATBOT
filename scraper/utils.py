import time
import random
from functools import wraps
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """Validates if the given string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def rate_limiter(min_seconds: int = 1, max_seconds: int = 3):
    """Decorator to add a random sleep delay for rate limiting."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = random.uniform(min_seconds, max_seconds)
            time.sleep(delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def retry(max_attempts: int = 3, delay_seconds: int = 2):
    """Decorator to retry a function if it raises an exception."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise e
                    time.sleep(delay_seconds * attempts)
        return wrapper
    return decorator
