from haystack.components.embedders import OpenAIDocumentEmbedder

from src.components.document_embedder import initialize_document_embedder


def test_initialize_document_embedder() -> None:
    """
    Test the initialize_document_embedder function with valid parameters.
    """
    # Initialize the OpenAI Document Embedder
    embedder = initialize_document_embedder()

    # Assert that the returned object is an instance of OpenAIDocumentEmbedder
    assert isinstance(
        embedder, OpenAIDocumentEmbedder
    ), "Expected OpenAIDocumentEmbedder instance"


def test_initialize_document_embedder_invalid_model() -> None:
    """
    Test the initialize_document_embedder function with an invalid model name.
    """
    try:
        # Initialize the OpenAI Document Embedder with an empty model name
        initialize_document_embedder(model="")
    except ValueError as e:
        assert str(e) == "Model name cannot be empty."


def test_initialize_document_embedder_invalid_dimensions() -> None:
    """
    Test the initialize_document_embedder function with an invalid dimensions value.
    """
    try:
        # Initialize the OpenAI Document Embedder with a negative dimensions value
        initialize_document_embedder(dimensions=-10)
    except ValueError as e:
        assert str(e) == "Dimensions must be greater than 0."


def test_initialize_document_embedder_invalid_api_base_url() -> None:
    """
    Test the initialize_document_embedder function with an invalid API base URL.
    """
    try:
        # Initialize the OpenAI Document Embedder with an empty API base URL
        initialize_document_embedder(api_base_url="")
    except ValueError as e:
        assert str(e) == "API base URL cannot be empty."
