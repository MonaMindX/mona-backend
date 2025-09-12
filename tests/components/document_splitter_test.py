from haystack.components.preprocessors import DocumentSplitter

from src.components.document_splitter import initialize_document_splitter


def test_initialize_document_splitter() -> None:
    """
    Test the initialize_document_splitter function with valid parameters.
    """
    # Initialize the DocumentSplitter
    splitter = initialize_document_splitter()

    # Assert that the returned object is an instance of DocumentSplitter
    assert isinstance(splitter, DocumentSplitter), "Expected DocumentSplitter instance"


def test_initialize_document_splitter_invalid_split_by() -> None:
    """
    Test the initialize_document_splitter function with an invalid split_by value.
    """
    try:
        # Initialize the DocumentSplitter with an invalid split_by value
        initialize_document_splitter(split_by="invalid")  # type: ignore
    except ValueError as e:
        assert (
            str(e)
            == "split_by must be one of function, page, passage, period, word, line, sentence."
        )


def test_initialize_document_splitter_invalid_language() -> None:
    """
    Test the initialize_document_splitter function with an invalid language value.
    """
    try:
        # Initialize the DocumentSplitter with an invalid language value
        initialize_document_splitter(language="invalid")  # type: ignore
    except ValueError as e:
        assert str(e) == "Invalid language value. Expected one of: en, de."


def test_initialize_document_splitter_invalid_split_length() -> None:
    """
    Test the initialize_document_splitter function with an invalid split_length value.
    """
    try:
        # Initialize the DocumentSplitter with a negative split_length value
        initialize_document_splitter(split_length=-10)
    except ValueError as e:
        assert str(e) == "split_length must be greater than 0."


def test_initialize_document_splitter_invalid_split_overlap() -> None:
    """
    Test the initialize_document_splitter function with an invalid split_overlap value.
    """
    try:
        # Initialize the DocumentSplitter with a negative split_overlap value
        initialize_document_splitter(split_overlap=-10)
    except ValueError as e:
        assert str(e) == "split_overlap must be greater than or equal to 0."
