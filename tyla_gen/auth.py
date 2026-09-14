"""API authentication and key verification."""

import os
import logging

logger = logging.getLogger(__name__)


def verify_api_key(key: str) -> bool:
    """Verify API key against environment variable."""
    expected_key = os.getenv("TYLA_API_KEY")
    
    if not expected_key:
        logger.warning("TYLA_API_KEY not set in environment")
        return False
    
    return key == expected_key


def get_api_key() -> str:
    """Get API key from environment."""
    key = os.getenv("TYLA_API_KEY")
    if not key:
        logger.error("TYLA_API_KEY not configured")
        raise ValueError("API key not configured")
    return key
