"""
The DocumentRetriever retrieves documents from a PostgreSQL database using embeddings.
"""

from typing import Literal

from haystack_integrations.components.retrievers.pgvector import (
    PgvectorEmbeddingRetriever,
)
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore

from src.config.settings import document_store, settings


def initialize_document_retriever(
    document_store: PgvectorDocumentStore = document_store,
    vector_function: Literal[
        "cosine_similarity", "inner_product", "l2_distance"
    ] = settings.document_store_vector_function,
) -> PgvectorEmbeddingRetriever:
    """
    Initialize the PgvectorEmbeddingRetriever using the provided document store and embedding dimension.
    Args:
        document_store (PgvectorDocumentStore): The document store to retrieve documents from.
        vector_function (Literal): The similarity function to use for vector similarity.
    Returns:
        PgvectorEmbeddingRetriever: The initialized document retriever.
    """

    return PgvectorEmbeddingRetriever(
        document_store=document_store, vector_function=vector_function
    )
