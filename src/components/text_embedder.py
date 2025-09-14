"""
The text ebedding model computes the embeddings of user query for text retrieval.
"""

from haystack.components.embedders import OpenAITextEmbedder

from src.config.settings import settings


def initialize_text_embedder(
    model: str = settings.embedder_embedding_model,
    dimensions: int = settings.embedder_dimensions,
    api_base_url: str = settings.openai_api_base_url,
    timeout: float = settings.embedder_timeout,
) -> OpenAITextEmbedder:
    """
    Initialize the OpenAI Text Embedder and return it.

    Args:
        model (str): The model name for the OpenAI Document Embedder.
        dimensions (int, optional): The dimensionality of the embeddings. Defaults to None.
        api_base_url (str):
    """
    return OpenAITextEmbedder(
        model=model, dimensions=dimensions, api_base_url=api_base_url, timeout=timeout
    )
