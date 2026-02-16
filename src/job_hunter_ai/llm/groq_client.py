"""
Unified Groq LLM client using official Groq SDK.

This replaces the previous manual requests-based implementation.
"""

from typing import List, Dict, Optional
from groq import Groq

# Import from parent package
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from job_hunter_ai.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_TEMPERATURE,
    GROQ_TIMEOUT,
)


class GroqClientError(Exception):
    """Raised when Groq API calls fail."""
    pass


def call_groq(
    prompt: str,
    temperature: Optional[float] = None,
    model: Optional[str] = None,
) -> str:
    """
    Call Groq API with a single user prompt.

    Args:
        prompt: User prompt text
        temperature: Temperature for generation (default from config)
        model: Model name (default from config)

    Returns:
        Generated text response

    Raises:
        GroqClientError: If API key is missing or API call fails
    """
    if not GROQ_API_KEY:
        raise GroqClientError(
            "GROQ_API_KEY not set. Please set it in your .env file or environment."
        )

    client = Groq(api_key=GROQ_API_KEY)

    model_name = model or GROQ_MODEL
    temp = temperature if temperature is not None else GROQ_TEMPERATURE

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temp,
        )
        return response.choices[0].message.content

    except Exception as e:
        raise GroqClientError(f"Groq API call failed: {str(e)}") from e


def call_groq_with_messages(
    messages: List[Dict[str, str]],
    temperature: Optional[float] = None,
    model: Optional[str] = None,
) -> str:
    """
    Call Groq API with a full message history.

    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Temperature for generation (default from config)
        model: Model name (default from config)

    Returns:
        Generated text response

    Raises:
        GroqClientError: If API key is missing or API call fails
    """
    if not GROQ_API_KEY:
        raise GroqClientError(
            "GROQ_API_KEY not set. Please set it in your .env file or environment."
        )

    client = Groq(api_key=GROQ_API_KEY)

    model_name = model or GROQ_MODEL
    temp = temperature if temperature is not None else GROQ_TEMPERATURE

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temp,
        )
        return response.choices[0].message.content

    except Exception as e:
        raise GroqClientError(f"Groq API call failed: {str(e)}") from e
