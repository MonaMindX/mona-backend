"""
The document embedder computes the embeddings of a list of documents
and stores the obtained vectors in the embedding field of each document.
"""

from typing import Union

from haystack.components.embedders import OpenAIDocumentEmbedder

from src.config.settings import settings


def initialize_document_embedder(
    model: str = settings.document_embedder_embedding_model,
    dimensions: Union[int, None] = settings.document_embedder_dimensions,
    api_base_url: str = settings.openai_api_base_url,
    timeout: float = settings.document_embedder_timeout,
) -> OpenAIDocumentEmbedder:
    """
    Initialize the OpenAI Document Embedder and return it.

    Args:
        model (str): The model name for the OpenAI Document Embedder.
        dimensions (int, optional): The dimensionality of the embeddings. Defaults to None.
        api_base_url (str):
    """
    return OpenAIDocumentEmbedder(
        model=model, dimensions=dimensions, api_base_url=api_base_url, timeout=timeout
    )
