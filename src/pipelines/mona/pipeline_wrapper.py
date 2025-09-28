"""
Pipeline Wrapper for the query processing pipeline

This class wraps the indexing pipeline and provides API functionality.
"""

from typing import Any, Dict, Generator, List, Union, cast

from hayhooks import get_last_user_message  # pyright: ignore[reportUnknownVariableType]
from hayhooks import BasePipelineWrapper, log, streaming_generator
from hayhooks.open_webui import OpenWebUIEvent
from hayhooks.server.routers.openai import Message
from haystack import AsyncPipeline, Pipeline
from haystack.dataclasses.streaming_chunk import StreamingChunk

from src.pipelines.mona.pipeline import initialize_chat_pipeline


class PipelineWrapper(BasePipelineWrapper):
    def setup(self) -> None:
        """Initialize both sync and async pipelines."""
        log.debug("Setting up Mona pipeline wrapper")
        try:
            self.pipeline = cast(
                Pipeline,
                initialize_chat_pipeline(is_async=False),
            )
            self.async_pipeline = cast(
                AsyncPipeline,
                initialize_chat_pipeline(is_async=True),
            )
            log.debug("Pipeline wrapper setup completed successfully")
        except Exception as e:
            log.error("Failed to setup ppipeline wrapper: {}", e)
            raise

    def run_api(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        query: str,
    ) -> str:
        """
        Run the pipeline with the user query.

        Args:
            query: User query string

        Returns:
            response: Response data containing the llm reply

        Raises:
            Exception: If an unexpected error occurs during processing
        """
        try:
            results = self.pipeline.run(
                {
                    "query_classifier": {"query": query},
                    "router": {"original_query": query},
                }
            )

            # Get the LLM response
            llm_data = results.get("llm_generator", {})
            reply = (
                llm_data.get("replies", [None])[0]
                if llm_data.get("replies")
                else "Query processed with no response."
            )

            return reply

        except Exception as e:
            log.error("Error during chat app processing: {}", e)
            return "Sorry, I encountered an error processing your request."

    async def run_api_async(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        query: str,
    ) -> str:
        """
        Run the chat app pipeline asynchronously with conversation history support.

        Args:
            query: User query string

        Returns:
            response: Response data containing the llm reply

        Raises:
            Exception: If an unexpected error occurs during processing
        """
        try:
            results = await self.async_pipeline.run_async(
                {
                    "query_classifier": {"query": query},
                    "router": {"original_query": query},
                }
            )

            # Get the LLM response
            llm_data = results.get("llm_generator", {})
            reply = (
                llm_data.get("replies", [None])[0]
                if llm_data.get("replies")
                else "Query processed with no response."
            )

            return reply

        except Exception as e:
            log.error("Error during async chat app processing: {}", e)
            return "Sorry, I encountered an error processing your request."

    def run_chat_completion(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        model: str,
        messages: List[Union[Message, Dict[str, Any]]],
        body: Dict[str, Any],
    ) -> Union[str, Generator[StreamingChunk | OpenWebUIEvent | str, None, None]]:
        """
        OpenAI-compatible chat completion endpoint for OpenWebUI integration.

        Args:
            model: Model name (for compatibility, not used in pipeline)
            messages: List of chat messages in OpenAI format
            body: Request body with additional parameters

        Returns:
            Union[str, Generator]: Response string or streaming generator
        """
        try:
            # Extract the last user message
            query = get_last_user_message(messages)  # pyright: ignore[reportCallIssue]

            return streaming_generator(  # type: ignore[no-any-return]
                pipeline=self.pipeline,
                pipeline_run_args={
                    "query_classifier": {"query": query},
                    "router": {"original_query": query},
                },
            )

        except Exception as e:
            log.error("Error in OpenAI chat completion: {}", e)
            return "Error processing request, please try again."
