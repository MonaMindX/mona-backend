"""
Indexing Pipeline

This module contains the initialization function for the indexing pipeline.
"""

from typing import Union

from hayhooks import log
from haystack import AsyncPipeline, Pipeline
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore

from src.components.document_cleaner import initialize_document_cleaner
from src.components.document_embedder import initialize_document_embedder
from src.components.document_splitter import initialize_document_splitter
from src.components.document_writer import initialize_document_writer
from src.components.file_to_markdown_converter import FileToMarkdownConverter
from src.components.markdown_to_document_converter import MarkdownToDocumentConverter


def initialize_indexing_pipeline(
    is_async: bool, document_store: PgvectorDocumentStore
) -> Union[Pipeline, AsyncPipeline]:
    """
    Initialize the indexing pipeline.

    Args:
        is_async (bool): Whether to use asynchronous processing.
        document_store (PgvectorDocumentStore): The document store to use for indexing.
    """
    pipeline = AsyncPipeline() if is_async else Pipeline()

    try:
        log.debug("Initializing Pipeline Components")
        # Convert files to Markdown
        pipeline.add_component("file_to_markdown_converter", FileToMarkdownConverter())
        log.debug("Successfully initialized FileToMarkdownConverter")

        # Convert Markdown to Document
        pipeline.add_component(
            "markdown_to_document_converter", MarkdownToDocumentConverter()
        )
        log.debug("Successfully initialized  MarkdownToDocumentConverter")

        # Split documents into smaller chunks
        pipeline.add_component("document_splitter", initialize_document_splitter())
        log.debug("Successfully initialized  Document Splitter")

        # Clean documents
        pipeline.add_component("document_cleaner", initialize_document_cleaner())
        log.debug("Successfully initialized  Document Cleaner")

        # Embed documents
        pipeline.add_component("document_embedder", initialize_document_embedder())
        log.debug("Successfully initialized  Document Embedder")

        # Write documents to the document store
        pipeline.add_component(
            "document_writer", initialize_document_writer(document_store)
        )
        log.debug("Successfully initialized  Document Writer")
        log.debug("Successfully initialized Pipeline Components")

        pipeline.connect(
            "file_to_markdown_converter.markdowns",
            "markdown_to_document_converter.markdowns",
        )
        pipeline.connect(
            "markdown_to_document_converter.documents", "document_splitter.documents"
        )
        pipeline.connect("document_splitter.documents", "document_cleaner.documents")
        pipeline.connect("document_cleaner.documents", "document_embedder.documents")
        pipeline.connect("document_embedder.documents", "document_writer.documents")
        log.debug("Successfully connected Pipeline Components")

        return pipeline

    except Exception as e:
        log.error(f"Failed to initialize indexing pipeline: {str(e)}")
        raise e
