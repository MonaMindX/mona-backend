"""
Document Splitter divides a list of text documents into a list of shorter text documents.
"""

from typing import Literal

from haystack.components.preprocessors import DocumentSplitter

from src.config.settings import settings


def initialize_document_splitter(
    split_by: Literal[
        "function", "page", "passage", "period", "word", "line", "sentence"
    ] = settings.document_splitter_split_by,
    language: Literal["en", "de"] = settings.document_splitter_language,
    split_length: int = settings.document_splitter_split_length,
    split_overlap: int = settings.document_splitter_split_overlap,
) -> DocumentSplitter:
    """
    Initialize the DocumentSplitter component.

    Args:
        split_by: The method used to split documents.
        language: The language of the documents.
        split_length: The maximum length of each split document.
        split_overlap: The overlap between split documents.
    """
    return DocumentSplitter(
        split_by=split_by,
        language=language,
        split_length=split_length,
        split_overlap=split_overlap,
    )
