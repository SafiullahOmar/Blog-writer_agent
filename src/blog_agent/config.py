"""
Configuration module for the Blog Writing Agent.

Handles all configuration through environment variables and Pydantic Settings.
"""

import os
from typing import Optional, Literal
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Environment variables can be set directly or loaded from a .env file.
    """
    
    # API Keys
    groq_api_key: str = Field(..., description="Groq API key for LLM access")
    tavily_api_key: Optional[str] = Field(None, description="Tavily API key for web search")
    
    # LLM Settings
    llm_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Model to use for LLM calls"
    )
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for LLM responses"
    )
    
    # Research Settings
    max_search_queries: int = Field(
        default=10,
        ge=1,
        le=20,
        description="Maximum number of search queries to run"
    )
    max_results_per_query: int = Field(
        default=6,
        ge=1,
        le=10,
        description="Maximum results per search query"
    )
    
    # Recency Settings (defaults, can be overridden by router)
    open_book_recency_days: int = Field(default=7, description="Recency window for open_book mode")
    hybrid_recency_days: int = Field(default=45, description="Recency window for hybrid mode")
    closed_book_recency_days: int = Field(default=3650, description="Recency window for closed_book mode")
    
    # Output Settings
    output_dir: str = Field(default="output", description="Directory for output files")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def get_settings() -> Settings:
    """
    Get application settings.
    
    Returns:
        Settings object with all configuration values.
    
    Raises:
        ValidationError: If required settings are missing.
    """
    return Settings()


# Convenience function to get settings with defaults for missing API keys (for testing)
def get_settings_safe() -> Settings:
    """
    Get settings with fallback for missing required values.
    
    Use this for testing or when you want to check settings availability.
    """
    try:
        return get_settings()
    except Exception as e:
        print(f"Warning: Could not load settings: {e}")
        raise
