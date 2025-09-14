from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from haystack import Document

from src.pipelines.retrieval_mona.pipeline_wrapper import PipelineWrapper


def test_setup_success() -> None:
    """
    Test that setup initializes both sync and async pipelines successfully.
    """
    wrapper = PipelineWrapper()

    with (
        patch(
            "src.pipelines.retrieval_mona.pipeline_wrapper.initialize_retrieval_pipeline"
        ) as mock_init_pipeline,
        patch("src.pipelines.retrieval_mona.pipeline_wrapper.log") as mock_log,
    ):
        mock_sync_pipeline = MagicMock()
        mock_async_pipeline = MagicMock()

        # Configure the mock to return different pipelines based on is_async parameter
        def side_effect(is_async: bool) -> MagicMock:
            return mock_async_pipeline if is_async else mock_sync_pipeline

        mock_init_pipeline.side_effect = side_effect

        wrapper.setup()

        # Verify both pipelines were initialized
        assert mock_init_pipeline.call_count == 2
        mock_init_pipeline.assert_any_call(is_async=False)
        mock_init_pipeline.assert_any_call(is_async=True)

        # Verify pipelines were assigned correctly
        assert wrapper.pipeline == mock_sync_pipeline
        assert wrapper.async_pipeline == mock_async_pipeline

        # Verify logging
        mock_log.debug.assert_any_call("Setting up Mona Retrieval pipeline wrapper")
        mock_log.debug.assert_any_call("Pipeline wrapper setup completed successfully")


def test_setup_raises_exception() -> None:
    """
    Test that setup raises an exception if pipeline initialization fails.
    """
    wrapper = PipelineWrapper()
    error_message = "Initialization failed"

    with (
        patch(
            "src.pipelines.retrieval_mona.pipeline_wrapper.initialize_retrieval_pipeline",
            side_effect=RuntimeError(error_message),
        ) as mock_init_pipeline,
        patch("src.pipelines.retrieval_mona.pipeline_wrapper.log") as mock_log,
        pytest.raises(RuntimeError, match=error_message),
    ):
        wrapper.setup()

    mock_init_pipeline.assert_called_once_with(is_async=False)
    mock_log.error.assert_called_once_with(
        "Failed to setup pipeline wrapper: {}", mock_init_pipeline.side_effect
    )


def test_run_api_success() -> None:
    """
    Test that run_api successfully processes a query and returns documents.
    """
    wrapper = PipelineWrapper()
    query = "test query"
    expected_documents = [
        Document(content="Document 1"),
        Document(content="Document 2"),
    ]

    # Mock the pipeline with the correct return structure
    mock_pipeline = MagicMock()
    mock_pipeline.run.return_value = {
        "documents_retriever": {"documents": expected_documents}
    }
    wrapper.pipeline = mock_pipeline

    result = wrapper.run_api(query)

    # Verify pipeline was called with correct parameters
    mock_pipeline.run.assert_called_once_with({"text_embedder": {"text": query}})

    # Verify result
    assert result == expected_documents


def test_run_api_with_empty_results() -> None:
    """
    Test that run_api handles empty results gracefully.
    """
    wrapper = PipelineWrapper()
    query = "test query"

    # Mock the pipeline to return empty results with correct structure
    mock_pipeline = MagicMock()
    mock_pipeline.run.return_value = {"documents_retriever": {"documents": []}}
    wrapper.pipeline = mock_pipeline

    result = wrapper.run_api(query)

    # Verify pipeline was called
    mock_pipeline.run.assert_called_once_with({"text_embedder": {"text": query}})

    # Verify result is empty list
    assert result == []


def test_run_api_exception_handling() -> None:
    """
    Test that run_api handles exceptions properly.
    """
    wrapper = PipelineWrapper()
    query = "test query"
    error_message = "Pipeline execution failed"

    # Mock the pipeline to raise an exception
    mock_pipeline = MagicMock()
    mock_pipeline.run.side_effect = Exception(error_message)
    wrapper.pipeline = mock_pipeline

    with (
        patch("src.pipelines.retrieval_mona.pipeline_wrapper.log") as mock_log,
        pytest.raises(Exception, match=error_message),
    ):
        wrapper.run_api(query)

    mock_log.error.assert_called_once_with(
        "Error during file processing: {}", mock_pipeline.run.side_effect
    )


@pytest.mark.asyncio
async def test_run_api_async_success() -> None:
    """
    Test that run_api_async successfully processes a query and returns documents.
    """
    wrapper = PipelineWrapper()
    query = "test async query"
    expected_documents = [
        Document(content="Async Document 1"),
        Document(content="Async Document 2"),
    ]

    # Mock the async pipeline with the correct return structure
    mock_async_pipeline = AsyncMock()
    mock_async_pipeline.run_async.return_value = {
        "documents_retriever": {"documents": expected_documents}
    }
    wrapper.async_pipeline = mock_async_pipeline

    result = await wrapper.run_api_async(query)

    # Verify pipeline was called with correct parameters
    mock_async_pipeline.run_async.assert_called_once_with(
        {"text_embedder": {"text": query}}
    )

    # Verify result
    assert result == expected_documents


@pytest.mark.asyncio
async def test_run_api_async_with_empty_results() -> None:
    """
    Test that run_api_async handles empty results gracefully.
    """
    wrapper = PipelineWrapper()
    query = "test async query"

    # Mock the async pipeline to return empty results with correct structure
    mock_async_pipeline = AsyncMock()
    mock_async_pipeline.run_async.return_value = {
        "documents_retriever": {"documents": []}
    }
    wrapper.async_pipeline = mock_async_pipeline

    result = await wrapper.run_api_async(query)

    # Verify pipeline was called
    mock_async_pipeline.run_async.assert_called_once_with(
        {"text_embedder": {"text": query}}
    )

    # Verify result is empty list
    assert result == []


@pytest.mark.asyncio
async def test_run_api_async_exception_handling() -> None:
    """
    Test that run_api_async handles exceptions properly.
    """
    wrapper = PipelineWrapper()
    query = "test async query"
    error_message = "Async pipeline execution failed"

    # Mock the async pipeline to raise an exception
    mock_async_pipeline = AsyncMock()
    mock_async_pipeline.run_async.side_effect = Exception(error_message)
    wrapper.async_pipeline = mock_async_pipeline

    with (
        patch("src.pipelines.retrieval_mona.pipeline_wrapper.log") as mock_log,
        pytest.raises(Exception, match=error_message),
    ):
        await wrapper.run_api_async(query)

    mock_log.error.assert_called_once_with(
        "Error during file processing: {}", mock_async_pipeline.run_async.side_effect
    )


def test_run_api_with_different_query_types() -> None:
    """
    Test that run_api works with different query string types.
    """
    wrapper = PipelineWrapper()

    # Mock the pipeline with correct structure
    mock_pipeline = MagicMock()
    mock_pipeline.run.return_value = {"documents_retriever": {"documents": []}}
    wrapper.pipeline = mock_pipeline

    # Test with different query types
    queries = [
        "simple query",
        "query with special characters !@#$%",
        "very long query " * 100,
        "",  # empty string
    ]

    for query in queries:
        wrapper.run_api(query)
        mock_pipeline.run.assert_called_with({"text_embedder": {"text": query}})


@pytest.mark.asyncio
async def test_run_api_async_with_different_query_types() -> None:
    """
    Test that run_api_async works with different query string types.
    """
    wrapper = PipelineWrapper()

    # Mock the async pipeline with correct structure
    mock_async_pipeline = AsyncMock()
    mock_async_pipeline.run_async.return_value = {
        "documents_retriever": {"documents": []}
    }
    wrapper.async_pipeline = mock_async_pipeline

    # Test with different query types
    queries = [
        "simple async query",
        "async query with special characters !@#$%",
        "very long async query " * 100,
        "",  # empty string
    ]

    for query in queries:
        await wrapper.run_api_async(query)
        mock_async_pipeline.run_async.assert_called_with(
            {"text_embedder": {"text": query}}
        )
