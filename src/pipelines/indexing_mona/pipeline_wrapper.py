"""
Pipeline Wrapper for the indexing pipeline

This class wraps the indexing pipeline and provides API functionality.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union, cast

from hayhooks import BasePipelineWrapper, log
from haystack import AsyncPipeline, Pipeline
from pydantic import ValidationError

from src.config.settings import document_store
from src.pipelines.indexing_mona.pipeline import initialize_indexing_pipeline
from src.schemas.document import MonaDocument


class PipelineWrapper(BasePipelineWrapper):
    def setup(self) -> None:
        log.debug("Setting up Mona Indexer pipeline wrapper")
        try:
            self.pipeline = cast(
                Pipeline,
                initialize_indexing_pipeline(
                    is_async=False,
                    document_store=document_store,
                ),
            )
            self.async_pipeline = cast(
                AsyncPipeline,
                initialize_indexing_pipeline(
                    is_async=True,
                    document_store=document_store,
                ),
            )
            log.debug("Pipeline wrapper setup completed successfully")
        except Exception as e:
            log.error("Failed to setup pipeline wrapper: {}", e)
            raise

    def _create_temporary_files(self, files: List[Any]) -> List[str]:
        """
        Create temporary files from uploaded file objects.

        Args:
            files: List of file upload objects

        Returns:
            List of temporary file paths

        Raises:
            ValueError: If file format isn't supported
            OSError: If a file cannot be written
        """
        temp_files: List[str] = []

        try:
            for i, file_data in enumerate(files):
                log.debug("Processing file {} of {}", i + 1, len(files))

                # Handle different file input formats
                if hasattr(file_data, "file") and hasattr(file_data, "filename"):
                    # This is a file upload
                    log.debug(
                        "Detected file upload object with filename: {}",
                        file_data.filename,
                    )
                    content = file_data.file.read()
                    filename = file_data.filename
                    log.debug(
                        "Read {} bytes from uploaded file",
                        len(content) if content else 0,
                    )
                else:
                    error_msg = f"Unsupported file format: {type(file_data)}"
                    log.error(error_msg)
                    raise ValueError(error_msg)

                if not filename:
                    filename = "uploaded_file"
                    log.warning("No filename provided, using default: {}", filename)

                # Create temporary file
                log.debug("Creating temporary file for: {}", filename)
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=Path(filename).suffix,
                    prefix=f"upload_{Path(filename).stem}_",
                )

                # Write content to temporary file
                try:
                    if isinstance(content, str):
                        temp_file.write(content.encode("utf-8"))
                        log.debug(
                            "Wrote string content to temporary file: {}", temp_file.name
                        )
                    else:
                        temp_file.write(content)
                        log.debug(
                            "Wrote binary content to temporary file: {}", temp_file.name
                        )
                except Exception as e:
                    log.error("Failed to write content to temporary file: {}", e)
                    raise

                temp_file.close()
                temp_files.append(temp_file.name)
                log.debug("Successfully created temporary file: {}", temp_file.name)

        except Exception as e:
            # Clean up any files created before the error
            self._cleanup_temporary_files(temp_files)
            raise

        return temp_files

    def _parse_metadata_list(self, metadata_item: Union[str, List[str]]) -> List[str]:
        """
        Parse metadata that might be a JSON string or already a list.
        Args:
            metadata_item: Metadata item to parse
        Returns:
            List of parsed metadata items
        """
        if isinstance(metadata_item, str):
            try:
                parsed: Union[List[str], str] = json.loads(metadata_item)
                return parsed if isinstance(parsed, list) else [str(parsed)]
            except json.JSONDecodeError:
                return [metadata_item]
        else:
            return metadata_item

    def _extract_file_metadata(
        self, files: List[Any], temp_files: List[str]
    ) -> Tuple[List[str], List[int]]:
        """
        Extract file names and sizes from uploaded files and their temporary counterparts.

        Args:
            files: Original file upload objects
            temp_files: List of temporary file paths

        Returns:
            Tuple of (file_names, file_sizes)
        """
        file_names: List[str] = []
        file_sizes: List[int] = []

        for i, temp_file_path in enumerate(temp_files):
            # Get original filename from the files list
            file_data = files[i]
            if hasattr(file_data, "filename"):
                original_filename = file_data.filename
            else:
                original_filename = f"uploaded_file_{i}"

            file_names.append(original_filename)

            # Get file size from temporary file
            try:
                file_size = os.path.getsize(temp_file_path)
                file_sizes.append(file_size)
                log.debug("File: {}, Size: {} bytes", original_filename, file_size)
            except OSError as e:
                log.warning("Failed to get size for file {}: {}", temp_file_path, e)
                file_sizes.append(0)

        log.debug("Extracted {} file names and sizes", len(file_names))
        return file_names, file_sizes

    def _parse_metadata(
        self,
        files: List[Any],
        titles: List[str],
        summaries: Optional[List[str]] = None,
        document_types: Optional[List[str]] = None,
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Parse and normalize metadata lists.

        Args:
            files: List of files (for count)
            titles: List of titles
            summaries: Optional list of summaries
            document_types: Optional list of document types

        Returns:
            Tuple of (parsed_titles, parsed_summaries, parsed_document_types)
        """
        parsed_titles: List[str] = []
        parsed_summaries: List[str] = []
        parsed_document_types: List[str] = []

        # Parse titles
        for title_item in titles:
            parsed_titles.extend(self._parse_metadata_list(title_item))

        # Parse summaries
        if summaries:
            for summary_item in summaries:
                parsed_summaries.extend(self._parse_metadata_list(summary_item))
        else:
            parsed_summaries = ["Unknown"] * len(files)

        # Parse document_types
        if document_types:
            for doc_type_item in document_types:
                parsed_document_types.extend(self._parse_metadata_list(doc_type_item))
        else:
            parsed_document_types = ["Unknown"] * len(files)

        return parsed_titles, parsed_summaries, parsed_document_types

    def _create_mona_documents(
        self,
        files: List[Any],
        file_names: List[str],
        file_sizes: List[int],
        parsed_titles: List[str],
        parsed_summaries: List[str],
        parsed_document_types: List[str],
    ) -> List[MonaDocument]:
        """
        Create MonaDocument objects from parsed metadata.

        Args:
            files: List of files (for count)
            file_names: List of file names
            file_sizes: List of file sizes
            parsed_titles: List of parsed titles
            parsed_summaries: List of parsed summaries
            parsed_document_types: List of parsed document types

        Returns:
            List of MonaDocument objects

        Raises:
            ValidationError: If document validation fails
        """
        mona_docs: List[MonaDocument] = []
        for i in range(len(files)):
            try:
                mona_doc = MonaDocument(
                    title=parsed_titles[i],
                    summary=parsed_summaries[i] if parsed_summaries else None,
                    document_type=(
                        parsed_document_types[i] if parsed_document_types else None
                    ),
                    file_name=file_names[i],
                    file_size=file_sizes[i] if file_sizes else None,
                )
                mona_docs.append(mona_doc)
            except ValidationError as e:
                log.error("Validation failed for document {}: {}", i, e)
                raise ValueError(f"Invalid metadata for document {i}: {e}")

        return mona_docs

    def _cleanup_temporary_files(self, temp_files: List[str]) -> None:
        """
        Clean up temporary files.

        Args:
            temp_files: List of temporary file paths to clean up
        """
        log.debug("Starting cleanup of {} temporary files", len(temp_files))
        cleaned_count = 0
        for temp_file_path in temp_files:
            try:
                os.unlink(temp_file_path)
                cleaned_count += 1
                log.debug("Cleaned up temporary file: {}", temp_file_path)
            except OSError as e:
                log.warning(
                    "Failed to clean up temporary file {}: {}", temp_file_path, e
                )

        log.debug(
            "Cleanup completed: {}/{} temporary files removed",
            cleaned_count,
            len(temp_files),
        )

    def _run_pipeline(
        self, temp_files: List[str], mona_docs: List[MonaDocument]
    ) -> str:
        """
        Run the pipeline with prepared data.

        Args:
            temp_files: List of temporary file paths
            mona_docs: List of MonaDocument objects

        Returns:
            Success message with document count
        """
        result = self.pipeline.run(
            data={
                "file_to_markdown_converter": {"file_paths": temp_files},
                "markdown_to_document_converter": {
                    "metadata": mona_docs,
                },
            }
        )
        log.debug("Pipeline execution completed, processing results")

        # Get the number of documents written
        documents_written = result.get("document_writer", {}).get(
            "documents_written", 0
        )

        success_message = (
            "Successfully added {} documents to the knowledgebase.".format(
                documents_written
            )
        )
        log.debug(success_message)
        return success_message

    async def _run_async_pipeline(
        self, temp_files: List[str], mona_docs: List[MonaDocument]
    ) -> str:
        """
        Run the async pipeline with prepared data.

        Args:
            temp_files: List of temporary file paths
            mona_docs: List of MonaDocument objects

        Returns:
            Success message with document count
        """
        result = await self.async_pipeline.run_async(
            data={
                "file_to_markdown_converter": {"file_paths": temp_files},
                "markdown_to_document_converter": {
                    "metadata": mona_docs,
                },
            }
        )
        log.debug("Pipeline execution completed, processing results")

        # Get the number of documents written
        documents_written = result.get("document_writer", {}).get(
            "documents_written", 0
        )

        success_message = (
            "Successfully added {} documents to the knowledgebase.".format(
                documents_written
            )
        )
        log.debug(success_message)
        return success_message

    def run_api(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        files: List[Any],
        titles: List[str],
        summaries: Optional[List[str]] = None,
        document_types: Optional[List[str]] = None,
    ) -> str:
        """
        Run the pipeline with uploaded files.

        Args:
            files: List of file upload objects or dictionaries containing file data
            titles: List of titles for each document
            summaries: List of summaries for each document
            document_types: List of document types for each document

        Returns:
            response: Response data from the API call

        Raises:
            ValueError: If file format ins't supported
            ValidationError: If any of the input data is invalid
            OSError: If a file cannot be opened or read
            Exception: If an unexpected error occurs
        """
        log.debug("Starting file upload processing for {} files", len(files))
        temp_files: List[str] = []

        try:
            # Save uploaded files to temporary locations
            temp_files = self._create_temporary_files(files)

            log.debug(
                "Created {} temporary files, starting pipeline execution",
                len(temp_files),
            )

            # Extract file names and sizes from temporary files
            file_names, file_sizes = self._extract_file_metadata(files, temp_files)

            # Parse metadata lists
            parsed_titles, parsed_summaries, parsed_document_types = (
                self._parse_metadata(files, titles, summaries, document_types)
            )

            # Create Mona Document objects for metadata
            mona_docs = self._create_mona_documents(
                files,
                file_names,
                file_sizes,
                parsed_titles,
                parsed_summaries,
                parsed_document_types,
            )

            # Process the temporary files using existing pipeline
            return self._run_pipeline(temp_files, mona_docs)

        except Exception as e:
            log.error("Error during file processing: {}", e)
            raise

        finally:
            # Clean up temporary files
            self._cleanup_temporary_files(temp_files)

    async def run_api_async(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        files: List[Any],
        titles: List[str],
        summaries: Optional[List[str]] = None,
        document_types: Optional[List[str]] = None,
    ) -> str:
        """
        Run the pipeline with uploaded files.

        Args:
            files: List of file upload objects or dictionaries containing file data
            titles: List of titles for each document
            summaries: List of summaries for each document
            document_types: List of document types for each document

        Returns:
            response: Response data from the API call

        Raises:
            ValueError: If file format ins't supported
            ValidationError: If any of the input data is invalid
            OSError: If a file cannot be opened or read
            Exception: If an unexpected error occurs
        """
        log.debug("Starting file upload processing for {} files", len(files))
        temp_files: List[str] = []

        try:
            # Save uploaded files to temporary locations
            temp_files = self._create_temporary_files(files)

            log.debug(
                "Created {} temporary files, starting pipeline execution",
                len(temp_files),
            )

            # Extract file names and sizes from temporary files
            file_names, file_sizes = self._extract_file_metadata(files, temp_files)

            # Parse metadata lists
            parsed_titles, parsed_summaries, parsed_document_types = (
                self._parse_metadata(files, titles, summaries, document_types)
            )

            # Create Mona Document objects for metadata
            mona_docs = self._create_mona_documents(
                files,
                file_names,
                file_sizes,
                parsed_titles,
                parsed_summaries,
                parsed_document_types,
            )

            # Process the temporary files using existing pipeline
            return await self._run_async_pipeline(temp_files, mona_docs)

        except Exception as e:
            log.error("Error during file processing: {}", e)
            raise

        finally:
            # Clean up temporary files
            self._cleanup_temporary_files(temp_files)
