from unittest.mock import MagicMock, patch

import pytest
from haystack import component
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore

from src.pipelines.indexing_mona.pipeline import initialize_indexing_pipeline


def create_mock_component(name: str) -> MagicMock:
    """Creates a MagicMock that looks like a Haystack Component."""
    mock = MagicMock(spec=component)
    mock.__class__.__name__ = name
    return mock


def test_initialize_indexing_pipeline_creates_async_pipeline() -> None:
    """
    Test that initialize_indexing_pipeline creates an AsyncPipeline when is_async is True.
    """
    with (
        patch(
            "src.pipelines.indexing_mona.pipeline.AsyncPipeline"
        ) as mock_async_pipeline,
        patch("src.pipelines.indexing_mona.pipeline.Pipeline") as mock_sync_pipeline,
    ):
        mock_store = MagicMock(spec=PgvectorDocumentStore)

        # Call the function with is_async=True
        pipeline = initialize_indexing_pipeline(
            is_async=True, document_store=mock_store
        )

        # Assert that AsyncPipeline was called and Pipeline was not
        mock_async_pipeline.assert_called_once()
        mock_sync_pipeline.assert_not_called()

        # Assert that the returned object is the instance of the mocked AsyncPipeline
        assert pipeline == mock_async_pipeline.return_value

        # Assert all components were added and connected
        assert mock_async_pipeline.return_value.add_component.call_count == 6
        assert mock_async_pipeline.return_value.connect.call_count == 5


def test_initialize_indexing_pipeline_creates_sync_pipeline() -> None:
    """
    Test that initialize_indexing_pipeline creates a synchronous Pipeline
    when is_async is False.
    """
    with (
        patch(
            "src.pipelines.indexing_mona.pipeline.AsyncPipeline"
        ) as mock_async_pipeline,
        patch("src.pipelines.indexing_mona.pipeline.Pipeline") as mock_sync_pipeline,
    ):
        mock_store = MagicMock(spec=PgvectorDocumentStore)

        # Call the function with is_async=False
        pipeline = initialize_indexing_pipeline(
            is_async=False, document_store=mock_store
        )

        # Assert that AsyncPipeline was called and Pipeline was not
        mock_sync_pipeline.assert_called_once()
        mock_async_pipeline.assert_not_called()

        # Assert that the returned object is the instance of the mocked AsyncPipeline
        assert pipeline == mock_sync_pipeline.return_value

        # Assert all components were added and connected
        assert mock_sync_pipeline.return_value.add_component.call_count == 6
        assert mock_sync_pipeline.return_value.connect.call_count == 5


@pytest.mark.parametrize("is_async", [True, False])
def test_initialize_indexing_pipeline_raises_exception_on_component_failure(
    is_async: bool,
) -> None:
    """
    Should raise an exception if any component initialization function fails.
    """
    mock_document_store = MagicMock(spec=PgvectorDocumentStore)
    error_message = "Failed to initialize component"

    with (
        patch(
            "src.pipelines.indexing_mona.pipeline.initialize_document_splitter",
            side_effect=Exception(error_message),
        ) as mock_splitter,
        patch("src.pipelines.indexing_mona.pipeline.log") as mock_log,
        pytest.raises(Exception) as exc_info,
    ):
        initialize_indexing_pipeline(is_async, mock_document_store)

    assert error_message in str(exc_info.value)
    mock_splitter.assert_called_once()
    mock_log.error.assert_called_once_with(
        f"Failed to initialize indexing pipeline: {error_message}"
    )
