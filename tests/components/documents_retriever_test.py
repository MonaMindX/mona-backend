"""
Document Retriever Component Tests
"""

from typing import Literal

import pytest
from haystack_integrations.components.retrievers.pgvector import (
    PgvectorEmbeddingRetriever,
)

from src.components.document_store import initialize_document_store
from src.components.documents_retriever import initialize_document_retriever
from src.config.settings import document_store, settings


def test_initialize_document_retriever_with_defaults() -> None:
    """Test initialize_document_retriever with default parameters."""
    result = initialize_document_retriever()

    assert isinstance(result, PgvectorEmbeddingRetriever)
    assert result.document_store == document_store
    assert result.vector_function == settings.document_store_vector_function


def test_initialize_document_retriever_with_custom_document_store() -> None:
    """Test initialize_document_retriever with custom document store."""
    new_document_store = initialize_document_store(
        embedding_dimension=768,
        vector_function="inner_product",
        recreate_table=False,
        search_strategy="exact_nearest_neighbor",
    )
    result = initialize_document_retriever(document_store=new_document_store)

    assert isinstance(result, PgvectorEmbeddingRetriever)
    assert result.document_store == new_document_store
    assert result.vector_function == "cosine_similarity"


@pytest.mark.parametrize(
    "vector_function", ["cosine_similarity", "inner_product", "l2_distance"]
)
def test_initialize_document_retriever_with_different_vector_functions(
    vector_function: Literal["cosine_similarity", "inner_product", "l2_distance"],
) -> None:
    """Test initialize_document_retriever with different vector functions."""
    result = initialize_document_retriever(
        document_store=document_store, vector_function=vector_function
    )

    assert isinstance(result, PgvectorEmbeddingRetriever)
    assert result.document_store == document_store
    assert result.vector_function == vector_function


def test_initialize_document_retriever_with_none_document_store() -> None:
    """Test behavior when document_store is None (edge case)."""

    # This should work with None as the function has a default
    try:
        initialize_document_retriever(
            document_store=None  # pyright: ignore[reportArgumentType]
        )
    except ValueError as e:
        assert str(e) == "document_store must be an instance of PgvectorDocumentStore"


def test_initialize_document_retriever_with_none_vector_function() -> None:
    """Test behavior when vector_function is None (edge case)."""
    try:
        initialize_document_retriever(
            document_store=document_store,
            vector_function=None,  # type: ignore[arg-type]
        )
    except ValueError as e:
        assert str(e) == "vector_function must be a valid vector function"


def test_initialize_document_retriever_with_empty_vector_function() -> None:
    """Test behavior when vector_function is an empty string (edge case)."""
    try:
        initialize_document_retriever(
            document_store=document_store,
            vector_function="",  # type: ignore[arg-type]
        )
    except ValueError as e:
        assert str(e) == "vector_function must be a valid vector function"


def test_initialize_document_retriever_with_invalid_vector_function() -> None:
    """Test behavior when vector_function is an invalid value (edge case)."""
    try:
        initialize_document_retriever(
            document_store=document_store,
            vector_function="invalid_function",  # type: ignore[arg-type]
        )
    except ValueError as e:
        assert (
            str(e)
            == "vector_function must be one of ['cosine_similarity', 'inner_product', 'l2_distance']"
        )


def test_initialize_document_retriever_with_non_pgvector_document_store() -> None:
    """Test behavior when document_store is not an instance of PgvectorDocumentStore (edge case)."""
    try:
        initialize_document_retriever(
            document_store="invalid_document_store"  # pyright: ignore[reportArgumentType]
        )
    except ValueError as e:
        assert str(e) == "document_store must be an instance of PgvectorDocumentStore"
