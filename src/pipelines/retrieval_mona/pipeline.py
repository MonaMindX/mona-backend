"""
Retrieval Pipeline

This module contains the initialization function for the retrieval pipeline.
"""

from typing import Union

from hayhooks import log
from haystack import AsyncPipeline, Pipeline

from src.components.documents_retriever import initialize_document_retriever
from src.components.text_embedder import initialize_text_embedder


def initialize_retrieval_pipeline(is_async: bool) -> Union[Pipeline, AsyncPipeline]:
    """
    Initialize the retrieval pipeline.

    Args:
        is_async (bool): Whether to use asynchronous processing.
    """
    pipeline = AsyncPipeline() if is_async else Pipeline()

    try:
        log.debug("Initializing Pipeline Components")
        # Embed user query
        pipeline.add_component("text_embedder", initialize_text_embedder())
        log.debug("Successfully initialized text_embedder")

        # Retrieve documents
        pipeline.add_component("documents_retriever", initialize_document_retriever())
        log.debug("Successfully initialized  documents_retriever")
        log.debug("Successfully initialized Pipeline Components")

        pipeline.connect(
            "text_embedder.embedding",
            "documents_retriever.query_embedding",
        )
        log.debug("Successfully connected Pipeline Components")

        return pipeline

    except Exception as e:
        log.error(f"Failed to initialize retrieval pipeline: {str(e)}")
        raise e
