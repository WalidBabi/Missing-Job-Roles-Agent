"""
Factory for creating LLM instances based on configuration
"""
from django.conf import settings
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic


def get_llm(temperature: float = None):
    """
    Get configured LLM instance
    
    Args:
        temperature: Override default temperature
    
    Returns:
        LangChain LLM instance
    """
    ai_config = settings.AI_CONFIG
    provider = ai_config.get('PROVIDER', 'openai')
    model = ai_config.get('MODEL', 'gpt-4')
    temp = temperature if temperature is not None else ai_config.get('TEMPERATURE', 0.2)
    
    if provider == 'openai':
        api_key = ai_config.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not configured in settings")
        
        return ChatOpenAI(
            model=model,
            temperature=temp,
            api_key=api_key
        )
    
    elif provider == 'anthropic':
        api_key = ai_config.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured in settings")
        
        return ChatAnthropic(
            model=model,
            temperature=temp,
            api_key=api_key
        )
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

