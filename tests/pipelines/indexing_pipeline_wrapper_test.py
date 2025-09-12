import io
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from haystack import AsyncPipeline, Pipeline

from src.pipelines.indexing_mona.pipeline_wrapper import PipelineWrapper
from src.schemas.document import MonaDocument


class DummyUpload:
    def __init__(self, content: bytes, filename: str = "test.txt"):
        self.file = io.BytesIO(content)
        self.filename = filename


class DummyUploadString:
    def __init__(self, content: str, filename: str = "test.txt"):
        self.file = io.StringIO(content)
        self.filename = filename


def test_setup_initializes_pipeline() -> None:
    """
    Test the setup method initializes the pipeline.
    """
    wrapper = PipelineWrapper()
    wrapper.setup()

    assert isinstance(wrapper.pipeline, Pipeline)
    assert isinstance(wrapper.async_pipeline, AsyncPipeline)


def test_create_temporary_files_creates_files() -> None:
    """
    Test the create_temporary_files method creates files.
    """
    f = DummyUpload(b"hello world", "file1.txt")
    wrapper = PipelineWrapper()
    temp_files = wrapper._create_temporary_files(  # pyright: ignore[reportPrivateUsage]
        [f]
    )

    assert len(temp_files) == 1
    assert os.path.exists(temp_files[0])
    with open(temp_files[0], "rb") as fh:
        assert fh.read() == b"hello world"

    wrapper._cleanup_temporary_files(temp_files)  # pyright: ignore[reportPrivateUsage]


def test_create_temporary_files_with_string_content() -> None:
    """
    Test _create_temporary_files with string content.
    """
    wrapper = PipelineWrapper()
    string_content = "this is a string"
    file_upload = DummyUploadString(string_content, "string.txt")

    temp_files = wrapper._create_temporary_files(  # pyright: ignore[reportPrivateUsage]
        [file_upload]
    )

    assert len(temp_files) == 1
    assert os.path.exists(temp_files[0])

    with open(temp_files[0], "rb") as f:
        assert f.read() == string_content.encode("utf-8")

    wrapper._cleanup_temporary_files(temp_files)  # pyright: ignore[reportPrivateUsage]


def test_create_temporary_files_unsupported_input() -> None:
    """
    Test the create_temporary_files method raises an error for unsupported inputs.
    """
    wrapper = PipelineWrapper()
    with pytest.raises(ValueError):
        wrapper._create_temporary_files(  # pyright: ignore[reportPrivateUsage]
            [{"foo": "bar"}]
        )


@patch("tempfile.NamedTemporaryFile")
def test_create_temporary_files_write_error(mock_named_temp_file: MagicMock) -> None:
    """
    Test _create_temporary_files when writing to the temp file fails.
    """
    mock_file = MagicMock()
    mock_file.write.side_effect = OSError("Disk full")
    mock_named_temp_file.return_value = mock_file

    wrapper = PipelineWrapper()
    files = [DummyUpload(b"abc", "test.txt")]

    with pytest.raises(OSError, match="Disk full"):
        wrapper._create_temporary_files(files)  # pyright: ignore[reportPrivateUsage]

    mock_file.close.assert_not_called()


def test_parse_metadata_list_with_json() -> None:
    """
    Test the parse_metadata_list method with JSON.
    """
    wrapper = PipelineWrapper()

    assert wrapper._parse_metadata_list(  # pyright: ignore[reportPrivateUsage]
        '["a","b"]'
    ) == [
        "a",
        "b",
    ]


def test_parse_metadata_list_invalid_json() -> None:
    """
    Test the parse_metadata_list method with invalid JSON.
    """
    wrapper = PipelineWrapper()
    assert wrapper._parse_metadata_list(  # pyright: ignore[reportPrivateUsage]
        "notjson"
    ) == ["notjson"]


def test_parse_metadata_list_already_list() -> None:
    """
    Test the parse_metadata_list method with already a list.
    """
    wrapper = PipelineWrapper()
    assert wrapper._parse_metadata_list(  # pyright: ignore[reportPrivateUsage]
        ["x"]
    ) == ["x"]


def test_extract_file_metadata() -> None:
    """
    Test the extract_file_metadata method.
    """
    upload = DummyUpload(b"abc", "doc.txt")
    wrapper = PipelineWrapper()
    temp_files = wrapper._create_temporary_files(  # pyright: ignore[reportPrivateUsage]
        [upload]
    )
    file_names, file_sizes = (
        wrapper._extract_file_metadata(  # pyright: ignore[reportPrivateUsage]
            [upload], temp_files
        )
    )

    assert file_names == ["doc.txt"]
    assert file_sizes[0] > 0

    wrapper._cleanup_temporary_files(temp_files)  # pyright: ignore[reportPrivateUsage]


def test_extract_file_metadata_no_filename() -> None:
    """
    Test _extract_file_metadata for a file object without a 'filename' attribute.
    """
    wrapper = PipelineWrapper()
    # Simulate a file object that lacks the .filename attribute
    files_without_filename: List[Dict[Any, Any]] = [
        {}
    ]  # An object that doesn't have .filename

    # Create a dummy temporary file to pass to the function
    temp_file = Path("temp_file.txt")
    temp_file.write_text("content")
    temp_files = [str(temp_file)]

    # Call the method directly
    file_names, file_sizes = (
        wrapper._extract_file_metadata(  # pyright: ignore[reportPrivateUsage]
            files_without_filename, temp_files
        )
    )

    # Assert that the default filename is created
    assert file_names == ["uploaded_file_0"]
    assert file_sizes == [len("content")]


def test_parse_metadata_defaults() -> None:
    """
    Test the parse_metadata method with default values.
    """
    wrapper = PipelineWrapper()
    files = [DummyUpload(b"abc", "a.txt"), DummyUpload(b"def", "b.txt")]
    titles = ["TitleA", "TitleB"]

    (
        parsed_titles,
        parsed_summaries,
        parsed_types,
    ) = wrapper._parse_metadata(  # pyright: ignore[reportPrivateUsage]
        files, titles
    )

    assert parsed_titles == ["TitleA", "TitleB"]
    assert parsed_summaries == ["Unknown", "Unknown"]
    assert parsed_types == ["Unknown", "Unknown"]


def test_parse_metadata_with_all_fields() -> None:
    """
    Test the parse_metadata method with all optional fields provided.
    """
    wrapper = PipelineWrapper()
    files = [DummyUpload(b"abc", "a.txt"), DummyUpload(b"def", "b.txt")]
    titles = ["TitleA", "TitleB"]
    summaries = ['["SummaryA", "SummaryB"]']  # JSON string list
    document_types = ["TypeA", "TypeB"]

    parsed_titles, parsed_summaries, parsed_types = (
        wrapper._parse_metadata(  # pyright: ignore[reportPrivateUsage]
            files, titles, summaries, document_types
        )
    )

    assert parsed_titles == ["TitleA", "TitleB"]
    assert parsed_summaries == ["SummaryA", "SummaryB"]
    assert parsed_types == ["TypeA", "TypeB"]


def test_create_mona_documents_valid() -> None:
    """
    Test the _create_mona_documents method with valid inputs.
    """
    wrapper = PipelineWrapper()

    files = [DummyUpload(b"abc", "x.txt")]
    docs = wrapper._create_mona_documents(  # pyright: ignore[reportPrivateUsage]
        files,
        ["x.txt"],
        [3],
        ["TitleX"],
        ["SummaryX"],
        ["TypeX"],
    )

    assert isinstance(docs, list)
    assert all(isinstance(doc, MonaDocument) for doc in docs)


def test_create_mona_documents_invalid() -> None:
    """
    Test the _create_mona_documents method with invalid inputs.
    """
    wrapper = PipelineWrapper()

    with pytest.raises(ValueError) as e:
        wrapper._create_mona_documents(  # pyright: ignore[reportPrivateUsage]
            [DummyUpload(b"abc")],
            ["file"],
            ["small file"],  # type: ignore
            ["Bad"],
            ["Bad"],
            ["Bad"],
        )

    assert "Invalid metadata for document 0" in str(e.value)
    assert "Input should be a valid integer" in str(e.value)


def test_cleanup_temp_files() -> None:
    """
    Test the _cleanup_temporary_files method.
    """
    wrapper = PipelineWrapper()
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(b"test")
    f.close()
    assert os.path.exists(f.name)

    wrapper._cleanup_temporary_files([f.name])  # pyright: ignore[reportPrivateUsage]
    assert not os.path.exists(f.name)


def test_run_pipeline_returns_success() -> None:
    """
    Test the _run_pipeline method with successful execution.
    """
    wrapper = PipelineWrapper()
    wrapper.pipeline = MagicMock()
    wrapper.pipeline.run.return_value = {"document_writer": {"documents_written": 2}}

    result = wrapper._run_pipeline(  # pyright: ignore[reportPrivateUsage]
        ["/tmp/file"], [MagicMock()]  # trunk-ignore(bandit/B108)
    )
    assert "Successfully added 2 documents" in result


@pytest.mark.asyncio
async def test_run_async_pipeline_returns_success() -> None:
    """
    Test the _run_async_pipeline method with successful execution.
    """
    wrapper = PipelineWrapper()
    wrapper.async_pipeline = MagicMock()
    wrapper.async_pipeline.run_async = AsyncMock(
        return_value={"document_writer": {"documents_written": 3}}
    )

    result = await wrapper._run_async_pipeline(  # pyright: ignore[reportPrivateUsage]
        ["/tmp/file"], [MagicMock()]  # trunk-ignore(bandit/B108)
    )
    assert "Successfully added 3 documents" in result


@patch("src.pipelines.indexing_mona.pipeline_wrapper.initialize_indexing_pipeline")
def test_setup_raises_exception(mock_init_pipeline: MagicMock) -> None:
    """
    Test that setup raises an exception if pipeline initialization fails.
    """
    wrapper = PipelineWrapper()
    mock_init_pipeline.side_effect = RuntimeError("Initialization failed")

    with pytest.raises(RuntimeError, match="Initialization failed"):
        wrapper.setup()


def test_create_temporary_files_no_filename() -> None:
    """
    Test _create_temporary_files with a file that has no filename.
    """
    f = DummyUpload(b"hello world", "")
    wrapper = PipelineWrapper()
    temp_files = wrapper._create_temporary_files(  # pyright: ignore[reportPrivateUsage]
        [f]
    )

    assert len(temp_files) == 1
    assert os.path.exists(temp_files[0])
    assert "upload_uploaded_file_" in os.path.basename(temp_files[0])

    wrapper._cleanup_temporary_files(temp_files)  # pyright: ignore[reportPrivateUsage]


@patch("os.path.getsize")
def test_extract_file_metadata_os_error(mock_getsize: MagicMock) -> None:
    """
    Test _extract_file_metadata when os.path.getsize raises an OSError.
    """
    mock_getsize.side_effect = OSError("File not found")
    wrapper = PipelineWrapper()
    files = [DummyUpload(b"abc", "doc.txt")]
    # trunk-ignore(bandit/B108)
    temp_files = ["/tmp/dummy_file"]

    file_names, file_sizes = (
        wrapper._extract_file_metadata(  # pyright: ignore[reportPrivateUsage]
            files, temp_files
        )
    )

    assert file_names == ["doc.txt"]
    assert file_sizes == [0]


@patch("os.unlink")
def test_cleanup_temp_files_os_error(mock_unlink: MagicMock) -> None:
    """
    Test _cleanup_temporary_files when os.unlink raises an OSError.
    """
    mock_unlink.side_effect = OSError("Permission denied")
    wrapper = PipelineWrapper()
    # The test should not raise an exception
    wrapper._cleanup_temporary_files(  # pyright: ignore[reportPrivateUsage]
        ["/tmp/dummy_file"]  # trunk-ignore(bandit/B108)
    )
    # trunk-ignore(bandit/B108)
    mock_unlink.assert_called_once_with("/tmp/dummy_file")


@patch("src.pipelines.indexing_mona.pipeline_wrapper.PipelineWrapper._run_pipeline")
def test_run_api_integration(mock_run_pipeline: MagicMock) -> None:
    """
    Test the run_api method as an integration test.
    """
    wrapper = PipelineWrapper()
    mock_run_pipeline.return_value = "Success"
    files = [DummyUpload(b"abc", "test.txt")]
    titles = ["Test Title"]

    result = wrapper.run_api(files, titles)

    assert result == "Success"
    mock_run_pipeline.assert_called_once()


@pytest.mark.asyncio
@patch(
    "src.pipelines.indexing_mona.pipeline_wrapper.PipelineWrapper._run_async_pipeline"
)
async def test_run_api_async_integration(mock_run_async_pipeline: AsyncMock) -> None:
    """
    Test the run_api_async method as an integration test.
    """
    wrapper = PipelineWrapper()
    mock_run_async_pipeline.return_value = "Success"
    files = [DummyUpload(b"abc", "test.txt")]
    titles = ["Test Title"]

    result = await wrapper.run_api_async(files, titles)

    assert result == "Success"
    mock_run_async_pipeline.assert_called_once()


@patch(
    "src.pipelines.indexing_mona.pipeline_wrapper.PipelineWrapper._create_temporary_files"
)
def test_run_api_exception_handling(mock_create_files: MagicMock) -> None:
    """Test that run_api handles generic exceptions."""
    wrapper = PipelineWrapper()
    mock_create_files.side_effect = Exception("Unexpected error")

    f = DummyUpload(b"hello", "test.txt")
    with pytest.raises(Exception, match="Unexpected error"):
        wrapper.run_api([f], ["Title"])


@pytest.mark.asyncio
@patch(
    "src.pipelines.indexing_mona.pipeline_wrapper.PipelineWrapper._create_temporary_files"
)
async def test_run_api_async_exception_handling(mock_create_files: MagicMock) -> None:
    """Test that run_api_async handles generic exceptions."""
    wrapper = PipelineWrapper()
    mock_create_files.side_effect = Exception("Async unexpected error")

    f = DummyUpload(b"hello", "test.txt")
    with pytest.raises(Exception, match="Async unexpected error"):
        await wrapper.run_api_async([f], ["Title"])
