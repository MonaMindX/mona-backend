"""
The DocumentWriter writes (saves) the documents in the document store
"""

from haystack.components.writers import DocumentWriter
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore


def initialize_document_writer(document_store: PgvectorDocumentStore) -> DocumentWriter:
    """
    Initialize the DocumentWriter using the provided document store.

    Args:
        document_store (PgvectorDocumentStore): The document store to use for writing documents.
    """
    return DocumentWriter(document_store=document_store)
