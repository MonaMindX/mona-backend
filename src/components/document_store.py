"""
The DocumentStore uses PostgreSQL for storing and querying documents using the Pgvector extension.
It can be used for storing and retrieving documents in a vector space model
"""

from typing import Literal

from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore


def initialize_document_store(
    embedding_dimension: int,
    vector_function: Literal["cosine_similarity", "inner_product", "l2_distance"],
    recreate_table: bool,
    search_strategy: Literal["exact_nearest_neighbor", "hnsw"],
) -> PgvectorDocumentStore:
    """
    Initialize the PgvectorDocumentStore and return it.

    Args:
        embedding_dimension (int): The dimensionality of the document embeddings.
        vector_function (Literal): The similarity function to use for vector similarity.
        recreate_table (bool): Whether to recreate the table if it already exists.
        search_strategy (Literal): The search strategy to use for vector similarity.
    """
    return PgvectorDocumentStore(
        embedding_dimension=embedding_dimension,
        vector_function=vector_function,
        recreate_table=recreate_table,
        search_strategy=search_strategy,
    )
