from haystack.components.preprocessors import DocumentCleaner

from src.components.document_cleaner import initialize_document_cleaner


def test_initialize_document_cleaner() -> None:
    """
    Test the initialize_document_cleaner function.
    """
    # Initialize the DocumentCleaner component
    cleaner = initialize_document_cleaner()

    # Assert that the returned object is an instance of DocumentCleaner
    assert isinstance(cleaner, DocumentCleaner), "Expected DocumentCleaner instance"
