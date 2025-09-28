"""
Pipeline Wrapper for the retrieval pipeline

This class wraps the retrieval pipeline and provides API functionality.
"""

from typing import List, cast

from hayhooks import BasePipelineWrapper, log
from haystack import AsyncPipeline, Document, Pipeline

from src.pipelines.retrieval_mona.pipeline import initialize_retrieval_pipeline


class PipelineWrapper(BasePipelineWrapper):
    def setup(self) -> None:
        log.debug("Setting up Mona Retrieval pipeline wrapper")
        try:
            self.pipeline = cast(
                Pipeline,
                initialize_retrieval_pipeline(
                    is_async=False,
                ),
            )
            self.async_pipeline = cast(
                AsyncPipeline,
                initialize_retrieval_pipeline(
                    is_async=True,
                ),
            )
            log.debug("Pipeline wrapper setup completed successfully")
        except Exception as e:
            log.error("Failed to setup pipeline wrapper: {}", e)
            raise

    def run_api(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        query: str,
    ) -> List[Document]:
        """
        Run the pipeline with uploaded files.

        Args:
            query: Query string for the documenet retrieval

        Returns:
            response: Response data from the API call

        Raises:
            ValueError: If file format ins't supported
            Exception: If an unexpected error occurs
        """
        try:
            pipeline_results = self.pipeline.run({"text_embedder": {"text": query}})
            retrieved_documents = pipeline_results.get("documents_retriever", {})
            # Extract the documents list from the dictionary with proper typing
            documents = retrieved_documents.get("documents", [])
            return cast(List[Document], documents)

        except Exception as e:
            log.error("Error during file processing: {}", e)
            raise

    async def run_api_async(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        query: str,
    ) -> List[Document]:
        """
        Run the pipeline with uploaded files.

        Args:
            query: Query string for the document retrieval

        Returns:
            response: Response data from the API call

        Raises:
            ValueError: If file format ins't supported
            Exception: If an unexpected error occurs
        """
        try:
            pipeline_results = await self.async_pipeline.run_async(
                {"text_embedder": {"text": query}}
            )
            retrieved_documents = pipeline_results.get("documents_retriever", {})
            # Extract the documents list from the dictionary with proper typing
            documents = retrieved_documents.get("documents", [])
            return cast(List[Document], documents)

        except Exception as e:
            log.error("Error during file processing: {}", e)
            raise
