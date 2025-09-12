import os
import tempfile
from unittest import mock

import pytest

from src.components.file_to_markdown_converter import FileToMarkdownConverter


def create_temp_file(content: str, extension: str) -> str:
    """
    Create a temporary file with the given content and extension.
    Returns the path to the temporary file.
    """
    fd, path = tempfile.mkstemp(suffix=extension)
    with os.fdopen(fd, "w", encoding="utf-8") as tmp:
        tmp.write(content)
    return path


def test_file_to_markdown_converter_run_empty_file_paths() -> None:
    """
    Test the run method of FileToMarkdownConverter with an empty list of file paths.
    """
    # Create an instance of FileToMarkdownConverter
    converter = FileToMarkdownConverter()

    # Call the run_async method with an empty list of file paths
    result = converter.run([])

    # Assert that the result is an empty dictionary
    assert result == {"markdowns": []}, "Expected {'markdowns': []}"


def test_file_to_markdown_converter_run_unsupported_extensions() -> None:
    """
    Test the FileToMarkdownConverter with unsupported file types.
    """
    converter = FileToMarkdownConverter()
    file_paths = ["/path/to/file1.jpg"]
    with pytest.raises(ValueError, match="Unsupported file extension: .jpg"):
        converter.run(file_paths)


def test_file_to_markdown_converter_run_single_txt_file() -> None:
    """
    Test the FileToMarkdownConverter with a list containing a single .txt file.
    """
    # Arrange
    file_content = "This is the content of the test file."
    file_path = create_temp_file(file_content, ".txt")
    file_paths = [file_path]
    converter = FileToMarkdownConverter()

    # Act
    result = converter.run(file_paths)

    # Assert
    assert len(result["markdowns"]) == 1
    assert result["markdowns"][0] == file_content
    os.remove(file_path)


def test_file_to_markdown_converter_multiple_files() -> None:
    """
    Test the FileToMarkdownConverter with a list containing multiple files.
    """
    md_content = "markdown content"
    txt_content = "text content"
    pdf_content = "pdf content"

    # Create real temp files only for .md and .txt
    md_path = create_temp_file(md_content, ".md")
    txt_path = create_temp_file(txt_content, ".txt")

    # For other types only the path is needed, because the conversion is mocked.
    pdf_path = "/fake/path/to/file.pdf"

    file_paths = [
        md_path,
        txt_path,
        pdf_path,
    ]
    converter = FileToMarkdownConverter()

    # Configure the mock to return content for the PDF file.
    # .md and .txt files are read directly and do not trigger the mock.
    with mock.patch(
        "src.components.file_to_markdown_converter.MarkItDown.convert"
    ) as mock_convert:
        mock_convert.return_value = mock.Mock(text_content=pdf_content)

        # Act
        result = converter.run(file_paths)

    # Assert
    assert len(result["markdowns"]) == len(
        file_paths
    ), "Expected the same number of markdowns as file paths"
    assert md_content in result["markdowns"]
    assert txt_content in result["markdowns"]
    assert pdf_content in result["markdowns"]

    os.remove(md_path)
    os.remove(txt_path)


def test_file_to_markdown_converter_run_conversion_error() -> None:
    """
    Test that FileToMarkdownConverter raises a ValueError when markitdown conversion fails.
    """
    # Arrange
    file_path = "/fake/path/to/document.pdf"
    converter = FileToMarkdownConverter()
    error_message = "Conversion failed!"

    # Mock the convert method to raise an exception
    with mock.patch(
        "src.components.file_to_markdown_converter.MarkItDown.convert"
    ) as mock_convert:
        mock_convert.side_effect = Exception(error_message)

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            converter.run([file_path])

    # Check if the exception message is correct
    expected_error = f"Error converting file {file_path}: {error_message}"
    assert str(excinfo.value) == expected_error


@pytest.mark.asyncio
async def test_file_to_markdown_converter_run_async_empty_file_paths() -> None:
    """
    Test the run_async method of FileToMarkdownConverter with an empty list of file paths.
    """
    # Create an instance of FileToMarkdownConverter
    converter = FileToMarkdownConverter()

    # Call the run_async method with an empty list of file paths
    result = await converter.run_async([])

    # Assert that the result is an empty dictionary
    assert result == {"markdowns": []}, "Expected {'markdowns': []}"


@pytest.mark.asyncio
async def test_file_to_markdown_converter_run_async_unsupported_extensions() -> None:
    """
    Test the FileToMarkdownConverter with unsupported file types asynchronously.
    """
    converter = FileToMarkdownConverter()
    file_paths = ["/path/to/file1.jpg"]
    with pytest.raises(ValueError, match="Unsupported file extension: .jpg"):
        await converter.run_async(file_paths)


@pytest.mark.asyncio
async def test_file_to_markdown_converter_run_async_single_txt_file() -> None:
    """
    Test the FileToMarkdownConverter with a list containing a single .txt file asynchronously.
    """
    # Arrange
    file_content = "This is the content of the test file."
    file_path = create_temp_file(file_content, ".txt")
    file_paths = [file_path]
    converter = FileToMarkdownConverter()

    # Act
    result = await converter.run_async(file_paths)

    # Assert
    assert len(result["markdowns"]) == 1
    assert result["markdowns"][0] == file_content
    os.remove(file_path)


@pytest.mark.asyncio
async def test_file_to_markdown_converter_multiple_files_async() -> None:
    """
    Test the FileToMarkdownConverter with a list containing multiple files asynchronously.
    """
    md_content = "markdown content"
    txt_content = "text content"

    # Create real temp files only for .md and .txt
    md_path = create_temp_file(md_content, ".md")
    txt_path = create_temp_file(txt_content, ".txt")

    file_paths = [
        md_path,
        txt_path,
    ]
    converter = FileToMarkdownConverter()

    # Act
    result = await converter.run_async(file_paths)

    # Assert
    assert len(result["markdowns"]) == len(
        file_paths
    ), "Expected the same number of markdowns as file paths"
    assert md_content in result["markdowns"]
    assert txt_content in result["markdowns"]

    os.remove(md_path)
    os.remove(txt_path)


@pytest.mark.asyncio
async def test_file_to_markdown_converter_run_async_conversion_error() -> None:
    """
    Test that FileToMarkdownConverter raises a ValueError when markitdown conversion fails asynchronously.
    """
    # Arrange
    file_path = "/fake/path/to/document.pdf"
    converter = FileToMarkdownConverter()
    error_message = "Conversion failed!"

    # Mock the convert method to raise an exception
    with mock.patch(
        "src.components.file_to_markdown_converter.MarkItDown.convert"
    ) as mock_convert:
        mock_convert.side_effect = Exception(error_message)

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            await converter.run_async([file_path])

    # Check if the exception message is correct
    expected_error = f"Error converting file {file_path}: {error_message}"
    assert str(excinfo.value) == expected_error
