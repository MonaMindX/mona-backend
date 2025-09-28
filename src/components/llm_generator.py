"""
LLM Generator component for generating answers based on user queries.
"""

from haystack.components.generators import OpenAIGenerator

from src.config.settings import settings


def initialize_llm_generator(
    api_base_url: str = settings.openai_api_base_url,
    model: str = settings.llm_model,
    max_tokens: int = settings.llm_max_tokens,
    temperature: float = settings.llm_temperature,
    timeout: float = settings.llm_timeout,
) -> OpenAIGenerator:
    """
    Initialize the OpenAI Generator and return it.

    Args:
        api_base_url (str): OpenAI API Base Url
        model (str): OpenAI model to use for generating answers
        max_tokens (int, optional): Maximum number of tokens to generate.
        temperature (float, optional): Temperature for sampling.
    """
    return OpenAIGenerator(
        api_base_url=api_base_url,
        model=model,
        timeout=timeout,
        generation_kwargs={
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
    )
