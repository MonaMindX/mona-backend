from typing import Any, Dict, List, Union
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from hayhooks.server.routers.openai import Message

from src.pipelines.mona.pipeline_wrapper import PipelineWrapper


def test_setup_success() -> None:
    """
    Test that setup initializes both sync and async pipelines successfully.
    """
    wrapper = PipelineWrapper()

    with (
        patch(
            "src.pipelines.mona.pipeline_wrapper.initialize_chat_pipeline"
        ) as mock_init_pipeline,
        patch("src.pipelines.mona.pipeline_wrapper.log") as mock_log,
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
        mock_log.debug.assert_any_call("Setting up Mona pipeline wrapper")
        mock_log.debug.assert_any_call("Pipeline wrapper setup completed successfully")


def test_setup_raises_exception_when_pipeline_initialization_fails() -> None:
    """
    Test that setup raises an exception when pipeline initialization fails.
    """
    wrapper = PipelineWrapper()
    error_message = "Pipeline initialization failed"

    with (
        patch(
            "src.pipelines.mona.pipeline_wrapper.initialize_chat_pipeline",
            side_effect=RuntimeError(error_message),
        ) as mock_init_pipeline,
        patch("src.pipelines.mona.pipeline_wrapper.log") as mock_log,
        pytest.raises(RuntimeError, match=error_message),
    ):
        wrapper.setup()

    mock_init_pipeline.assert_called_once_with(is_async=False)
    mock_log.error.assert_called_once_with(
        "Failed to setup ppipeline wrapper: {}", mock_init_pipeline.side_effect
    )


def test_run_api_returns_llm_reply_with_valid_query() -> None:
    """
    Test that run_api returns the LLM reply when called with a valid query.
    """
    wrapper = PipelineWrapper()
    query = "What is artificial intelligence?"
    expected_reply = "Artificial intelligence is a field of computer science."

    # Mock the pipeline with the correct return structure
    mock_pipeline = MagicMock()
    mock_pipeline.run.return_value = {"llm_generator": {"replies": [expected_reply]}}
    wrapper.pipeline = mock_pipeline

    result = wrapper.run_api(query)

    # Verify pipeline was called with correct parameters
    mock_pipeline.run.assert_called_once_with(
        {
            "query_classifier": {"query": query},
            "router": {"original_query": query},
        }
    )

    # Verify result
    assert result == expected_reply


def test_run_api_returns_default_message_when_llm_generator_returns_empty_replies() -> (
    None
):
    """
    Test that run_api returns default message when LLM generator returns empty replies.
    """
    wrapper = PipelineWrapper()
    query = "test query"

    # Mock the pipeline to return empty replies
    mock_pipeline = MagicMock()
    mock_pipeline.run.return_value = {"llm_generator": {"replies": []}}
    wrapper.pipeline = mock_pipeline

    result = wrapper.run_api(query)

    # Verify pipeline was called with correct parameters
    mock_pipeline.run.assert_called_once_with(
        {
            "query_classifier": {"query": query},
            "router": {"original_query": query},
        }
    )

    # Verify default message is returned
    assert result == "Query processed with no response."


def test_run_api_pipeline_exception_handling() -> None:
    """
    Test that run_api returns error message when pipeline.run throws an exception.
    """
    wrapper = PipelineWrapper()
    query = "test query"
    error_message = "Pipeline execution failed"

    # Mock the pipeline to raise an exception
    mock_pipeline = MagicMock()
    mock_pipeline.run.side_effect = Exception(error_message)
    wrapper.pipeline = mock_pipeline

    with patch("src.pipelines.mona.pipeline_wrapper.log") as mock_log:
        result = wrapper.run_api(query)

    # Verify pipeline was called with correct parameters
    mock_pipeline.run.assert_called_once_with(
        {
            "query_classifier": {"query": query},
            "router": {"original_query": query},
        }
    )

    # Verify error handling
    mock_log.error.assert_called_once_with(
        "Error during chat app processing: {}", mock_pipeline.run.side_effect
    )

    # Verify result is error message
    assert result == "Sorry, I encountered an error processing your request."


@pytest.mark.asyncio
async def test_run_api_async_returns_llm_reply_with_valid_query() -> None:
    """
    Test that run_api_async returns LLM reply when called with a valid query.
    """
    wrapper = PipelineWrapper()
    query = "What is the weather today?"
    expected_reply = "The weather is sunny and warm."

    # Mock the async pipeline with the correct return structure
    mock_async_pipeline = AsyncMock()
    mock_async_pipeline.run_async.return_value = {
        "llm_generator": {"replies": [expected_reply]}
    }
    wrapper.async_pipeline = mock_async_pipeline

    result = await wrapper.run_api_async(query)

    # Verify pipeline was called with correct parameters
    mock_async_pipeline.run_async.assert_called_once_with(
        {
            "query_classifier": {"query": query},
            "router": {"original_query": query},
        }
    )

    # Verify result
    assert result == expected_reply


@pytest.mark.asyncio
async def test_run_api_async_returns_default_message_when_empty_replies() -> None:
    """
    Test that run_api_async returns default message when pipeline returns empty replies.
    """
    wrapper = PipelineWrapper()
    query = "test query"

    # Mock the async pipeline to return empty replies
    mock_async_pipeline = AsyncMock()
    mock_async_pipeline.run_async.return_value = {"llm_generator": {"replies": []}}
    wrapper.async_pipeline = mock_async_pipeline

    result = await wrapper.run_api_async(query)

    # Verify pipeline was called with correct parameters
    mock_async_pipeline.run_async.assert_called_once_with(
        {
            "query_classifier": {"query": query},
            "router": {"original_query": query},
        }
    )

    # Verify default message is returned when replies is empty
    assert result == "Query processed with no response."


@pytest.mark.asyncio
async def test_run_api_async_exception_handling() -> None:
    """
    Test that run_api_async returns error message when async_pipeline.run_async throws an exception.
    """
    wrapper = PipelineWrapper()
    query = "test query"
    error_message = "Async pipeline execution failed"

    # Mock the async pipeline to raise an exception
    mock_async_pipeline = AsyncMock()
    mock_async_pipeline.run_async.side_effect = Exception(error_message)
    wrapper.async_pipeline = mock_async_pipeline

    with patch("src.pipelines.mona.pipeline_wrapper.log") as mock_log:
        result = await wrapper.run_api_async(query)

    # Verify pipeline was called with correct parameters
    mock_async_pipeline.run_async.assert_called_once_with(
        {
            "query_classifier": {"query": query},
            "router": {"original_query": query},
        }
    )

    # Verify error message is returned
    assert result == "Sorry, I encountered an error processing your request."

    # Verify error was logged
    mock_log.error.assert_called_once_with(
        "Error during async chat app processing: {}",
        mock_async_pipeline.run_async.side_effect,
    )


def test_run_chat_completion_success() -> None:
    """
    Test that run_chat_completion extracts last user message and returns streaming generator.
    """
    wrapper = PipelineWrapper()
    model = "test-model"
    messages: List[Union[Message, Dict[str, Any]]] = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you!"},
        {"role": "user", "content": "What is the weather like?"},
    ]
    body: Dict[str, Any] = {"temperature": 0.7, "max_tokens": 100}

    # Mock the pipeline
    mock_pipeline = MagicMock()
    wrapper.pipeline = mock_pipeline

    with (
        patch(
            "src.pipelines.mona.pipeline_wrapper.get_last_user_message"
        ) as mock_get_message,
        patch(
            "src.pipelines.mona.pipeline_wrapper.streaming_generator"
        ) as mock_streaming_generator,
    ):
        mock_get_message.return_value = "What is the weather like?"
        mock_generator = MagicMock()
        mock_streaming_generator.return_value = mock_generator

        result = wrapper.run_chat_completion(model, messages, body)

        # Verify get_last_user_message was called with messages
        mock_get_message.assert_called_once_with(messages)

        # Verify streaming_generator was called with correct parameters
        mock_streaming_generator.assert_called_once_with(
            pipeline=mock_pipeline,
            pipeline_run_args={
                "query_classifier": {"query": "What is the weather like?"},
                "router": {"original_query": "What is the weather like?"},
            },
        )

        # Verify result is the streaming generator
        assert result == mock_generator


def test_run_chat_completion_get_last_user_message_failure() -> None:
    """
    Test that run_chat_completion returns error message when get_last_user_message fails.
    """
    wrapper = PipelineWrapper()
    model = "test-model"
    messages: List[Union[Message, Dict[str, Any]]] = [
        {"role": "user", "content": "test message"}
    ]
    body: Dict[str, Any] = {}

    # Mock the pipeline
    mock_pipeline = MagicMock()
    wrapper.pipeline = mock_pipeline

    with (
        patch(
            "src.pipelines.mona.pipeline_wrapper.get_last_user_message"
        ) as mock_get_message,
        patch("src.pipelines.mona.pipeline_wrapper.log") as mock_log,
    ):
        # Make get_last_user_message raise an exception
        error_message = "Failed to extract user message"
        mock_get_message.side_effect = Exception(error_message)

        result = wrapper.run_chat_completion(model, messages, body)

        # Verify the error message is returned
        assert result == "Error processing request, please try again."

        # Verify logging
        mock_log.error.assert_called_once_with(
            "Error in OpenAI chat completion: {}", mock_get_message.side_effect
        )

        # Verify streaming_generator was not called
        mock_pipeline.run.assert_not_called()
