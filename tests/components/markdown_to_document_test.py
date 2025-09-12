from typing import List

import pytest

from src.components.markdown_to_document_converter import MarkdownToDocumentConverter
from src.schemas.document import MonaDocument


def test_markdown_to_document_converter_run_success() -> None:
    """
    Test the run method of MarkdownToDocumentConverter with valid inputs.
    """
    # Arrange
    converter = MarkdownToDocumentConverter()
    markdowns = ["# Hello", "## World"]
    metadata = [
        MonaDocument(file_name="file1.md"),
        MonaDocument(file_name="file2.md"),
    ]

    # Act
    result = converter.run(markdowns, metadata)

    # Assert
    assert "documents" in result
    assert len(result["documents"]) == 2
    assert result["documents"][0].content == markdowns[0]
    assert result["documents"][0].meta == metadata[0].model_dump()
    assert result["documents"][1].content == markdowns[1]
    assert result["documents"][1].meta == metadata[1].model_dump()


def test_markdown_to_document_converter_run_mismatched_length() -> None:
    """
    Test that the run method raises ValueError for mismatched input lengths.
    """
    # Arrange
    converter = MarkdownToDocumentConverter()
    markdowns = ["# Hello"]
    metadata = [
        MonaDocument(file_name="file1.md"),
        MonaDocument(file_name="file2.md"),
    ]

    # Act & Assert
    with pytest.raises(ValueError, match="Number of markdowns .* must match"):
        converter.run(markdowns, metadata)


def test_markdown_to_document_converter_run_empty_lists() -> None:
    """
    Test the run method with empty lists, expecting an empty documents list.
    """
    # Arrange
    converter = MarkdownToDocumentConverter()
    markdowns: List[str] = []
    metadata: List[MonaDocument] = []

    # Act
    result = converter.run(markdowns, metadata)

    # Assert
    assert result == {"documents": []}


@pytest.mark.asyncio
async def test_markdown_to_document_converter_run_async_success() -> None:
    """
    Test the run_async method of MarkdownToDocumentConverter with valid inputs.
    """
    # Arrange
    converter = MarkdownToDocumentConverter()
    markdowns = ["# Async", "## Test"]
    metadata = [
        MonaDocument(file_name="file_async1.md"),
        MonaDocument(file_name="file_async2.md"),
    ]

    # Act
    result = await converter.run_async(markdowns, metadata)

    # Assert
    assert "documents" in result
    assert len(result["documents"]) == 2
    assert result["documents"][0].content == markdowns[0]
    assert result["documents"][0].meta == metadata[0].model_dump()
    assert result["documents"][1].content == markdowns[1]
    assert result["documents"][1].meta == metadata[1].model_dump()


@pytest.mark.asyncio
async def test_markdown_to_document_converter_run_async_mismatched_length() -> None:
    """
    Test that run_async raises ValueError for mismatched input lengths.
    """
    # Arrange
    converter = MarkdownToDocumentConverter()
    markdowns = ["# Async"]
    metadata = [
        MonaDocument(file_name="file_async1.md"),
        MonaDocument(file_name="file_async2.md"),
    ]

    # Act & Assert
    with pytest.raises(ValueError, match="Number of markdowns .* must match"):
        await converter.run_async(markdowns, metadata)


@pytest.mark.asyncio
async def test_markdown_to_document_converter_run_async_empty_lists() -> None:
    """
    Test the run_async method with empty lists, expecting an empty documents list.
    """
    # Arrange
    converter = MarkdownToDocumentConverter()
    markdowns: List[str] = []
    metadata: List[MonaDocument] = []

    # Act
    result = await converter.run_async(markdowns, metadata)

    # Assert
    assert result == {"documents": []}
