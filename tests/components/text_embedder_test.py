"""
Text Embedder Component Integration Tests
"""

import pytest
from haystack.components.embedders import OpenAITextEmbedder

from src.components.text_embedder import initialize_text_embedder
from src.config.settings import settings


def test_initialize_text_embedder_with_defaults() -> None:
    """Test initialize_text_embedder with default parameters from settings."""
    embedder = initialize_text_embedder()

    assert isinstance(embedder, OpenAITextEmbedder)
    assert embedder.model == settings.embedder_embedding_model
    assert embedder.dimensions == settings.embedder_dimensions
    assert embedder.api_base_url == settings.openai_api_base_url
    assert embedder.timeout == settings.embedder_timeout


def test_initialize_text_embedder_with_custom_model() -> None:
    """Test initialize_text_embedder with custom model parameter."""
    custom_model = "text-embedding-3-large"

    embedder = initialize_text_embedder(model=custom_model)

    assert isinstance(embedder, OpenAITextEmbedder)
    assert embedder.model == custom_model
    assert embedder.dimensions == settings.embedder_dimensions
    assert embedder.api_base_url == settings.openai_api_base_url
    assert embedder.timeout == settings.embedder_timeout


def test_initialize_text_embedder_with_custom_dimensions() -> None:
    """Test initialize_text_embedder with custom dimensions parameter."""
    custom_dimensions = 512

    embedder = initialize_text_embedder(dimensions=custom_dimensions)

    assert isinstance(embedder, OpenAITextEmbedder)
    assert embedder.model == settings.embedder_embedding_model
    assert embedder.dimensions == custom_dimensions
    assert embedder.api_base_url == settings.openai_api_base_url
    assert embedder.timeout == settings.embedder_timeout


def test_initialize_text_embedder_with_custom_api_base_url() -> None:
    """Test initialize_text_embedder with custom API base URL."""
    custom_api_base_url = "https://custom-api.openai.com/v1"

    embedder = initialize_text_embedder(api_base_url=custom_api_base_url)

    assert isinstance(embedder, OpenAITextEmbedder)
    assert embedder.model == settings.embedder_embedding_model
    assert embedder.dimensions == settings.embedder_dimensions
    assert embedder.api_base_url == custom_api_base_url
    assert embedder.timeout == settings.embedder_timeout


def test_initialize_text_embedder_with_custom_timeout() -> None:
    """Test initialize_text_embedder with custom timeout parameter."""
    custom_timeout = 60.0

    embedder = initialize_text_embedder(timeout=custom_timeout)

    assert isinstance(embedder, OpenAITextEmbedder)
    assert embedder.model == settings.embedder_embedding_model
    assert embedder.dimensions == settings.embedder_dimensions
    assert embedder.api_base_url == settings.openai_api_base_url
    assert embedder.timeout == custom_timeout


def test_initialize_text_embedder_with_all_custom_parameters() -> None:
    """Test initialize_text_embedder with all custom parameters."""
    custom_model = "text-embedding-3-small"
    custom_dimensions = 256
    custom_api_base_url = "https://test-api.openai.com/v1"
    custom_timeout = 45.0

    embedder = initialize_text_embedder(
        model=custom_model,
        dimensions=custom_dimensions,
        api_base_url=custom_api_base_url,
        timeout=custom_timeout,
    )

    assert isinstance(embedder, OpenAITextEmbedder)
    assert embedder.model == custom_model
    assert embedder.dimensions == custom_dimensions
    assert embedder.api_base_url == custom_api_base_url
    assert embedder.timeout == custom_timeout


def test_initialize_text_embedder_return_type_consistency() -> None:
    """Test that multiple calls return consistent OpenAITextEmbedder instances."""
    embedder1 = initialize_text_embedder()
    embedder2 = initialize_text_embedder()

    # Should be different instances
    assert embedder1 is not embedder2

    # But same type and configuration
    assert type(embedder1) == type(embedder2)
    assert embedder1.model == embedder2.model
    assert embedder1.dimensions == embedder2.dimensions
    assert embedder1.api_base_url == embedder2.api_base_url
    assert embedder1.timeout == embedder2.timeout


def test_initialize_text_embedder_with_invalid_api_base_url() -> None:
    """Test initialize_text_embedder with invalid API base URL format."""
    with pytest.raises((ValueError, Exception)):
        initialize_text_embedder(api_base_url=9999)  # type: ignore[arg-type]
