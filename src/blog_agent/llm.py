"""
LLM Client module for the Blog Writing Agent.

Provides a configured LLM instance for use throughout the application.
"""

from functools import lru_cache
from langchain_groq import ChatGroq

from blog_agent.config import get_settings


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    """
    Get a configured LLM instance.
    
    Uses lru_cache to ensure only one instance is created.
    
    Returns:
        Configured ChatGroq instance.
    """
    settings = get_settings()
    
    return ChatGroq(
        model=settings.llm_model,
        api_key=settings.groq_api_key,
        temperature=settings.llm_temperature,
    )


def get_llm_with_structured_output(schema):
    """
    Get an LLM instance configured for structured output.
    
    Args:
        schema: Pydantic model class for output structure.
        
    Returns:
        LLM instance bound to produce structured output.
    """
    llm = get_llm()
    return llm.with_structured_output(schema)
