from unittest.mock import MagicMock, patch

import pytest
from haystack import component

from src.pipelines.retrieval_mona.pipeline import initialize_retrieval_pipeline


def create_mock_component(name: str) -> MagicMock:
    """Creates a MagicMock that looks like a Haystack Component."""
    mock = MagicMock(spec=component)
    mock.__class__.__name__ = name
    return mock


def test_initialize_retrieval_pipeline_creates_async_pipeline() -> None:
    """
    Test that initialize_retrieval_pipeline creates an AsyncPipeline when is_async is True.
    """
    with (
        patch(
            "src.pipelines.retrieval_mona.pipeline.AsyncPipeline"
        ) as mock_async_pipeline,
        patch("src.pipelines.retrieval_mona.pipeline.Pipeline") as mock_sync_pipeline,
    ):
        # Call the function with is_async=True
        pipeline = initialize_retrieval_pipeline(is_async=True)

        # Assert that AsyncPipeline was called and Pipeline was not
        mock_async_pipeline.assert_called_once()
        mock_sync_pipeline.assert_not_called()

        # Assert that the returned object is the instance of the mocked AsyncPipeline
        assert pipeline == mock_async_pipeline.return_value

        # Assert all components were added and connected
        assert mock_async_pipeline.return_value.add_component.call_count == 2
        assert mock_async_pipeline.return_value.connect.call_count == 1


def test_initialize_retrieval_pipeline_creates_sync_pipeline() -> None:
    """
    Test that initialize_retrieval_pipeline creates a synchronous Pipeline
    when is_async is False.
    """
    with (
        patch(
            "src.pipelines.retrieval_mona.pipeline.AsyncPipeline"
        ) as mock_async_pipeline,
        patch("src.pipelines.retrieval_mona.pipeline.Pipeline") as mock_sync_pipeline,
    ):
        # Call the function with is_async=False
        pipeline = initialize_retrieval_pipeline(is_async=False)

        # Assert that Pipeline was called and AsyncPipeline was not
        mock_sync_pipeline.assert_called_once()
        mock_async_pipeline.assert_not_called()

        # Assert that the returned object is the instance of the mocked Pipeline
        assert pipeline == mock_sync_pipeline.return_value

        # Assert all components were added and connected
        assert mock_sync_pipeline.return_value.add_component.call_count == 2
        assert mock_sync_pipeline.return_value.connect.call_count == 1


@pytest.mark.parametrize("is_async", [True, False])
def test_initialize_retrieval_pipeline_raises_exception_on_component_failure(
    is_async: bool,
) -> None:
    """
    Should raise an exception if any component initialization function fails.
    """
    error_message = "Failed to initialize component"

    with (
        patch(
            "src.pipelines.retrieval_mona.pipeline.initialize_text_embedder",
            side_effect=Exception(error_message),
        ) as mock_text_embedder,
        patch("src.pipelines.retrieval_mona.pipeline.log") as mock_log,
        pytest.raises(Exception) as exc_info,
    ):
        initialize_retrieval_pipeline(is_async)

    assert error_message in str(exc_info.value)
    mock_text_embedder.assert_called_once()
    mock_log.error.assert_called_once_with(
        f"Failed to initialize retrieval pipeline: {error_message}"
    )
