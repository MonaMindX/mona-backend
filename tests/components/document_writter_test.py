from haystack.components.writers import DocumentWriter
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore

from src.components.document_writer import initialize_document_writer


def test_initialize_document_writer() -> None:
    """
    Test the initialize_document_writer function with a valid document store.
    """
    # Initialize the PgvectorDocumentStore
    document_store = PgvectorDocumentStore()

    # Initialize the DocumentWriter
    writer = initialize_document_writer(document_store=document_store)

    # Assert that the returned object is an instance of DocumentWriter
    assert isinstance(writer, DocumentWriter), "Expected DocumentWriter instance"


def test_initialize_document_writer_none_document_store() -> None:
    """
    Test the initialize_document_writer function with a None document store.
    """
    try:
        # Initialize the DocumentWriter with a None document store
        initialize_document_writer(
            document_store=None  # pyright: ignore[reportArgumentType]
        )
    except ValueError as e:
        assert str(e) == "Document store cannot be None."
