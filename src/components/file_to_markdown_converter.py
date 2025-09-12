"""
The FileToMarkdownConverters convert md, txt, pdf, docx, pptx, xlsx and xls files to markdown format.
"""

import asyncio
import os
from typing import Dict, List

from haystack import component
from markitdown import MarkItDown


@component
class FileToMarkdownConverter:
    """
    Convert a file to markdown format.
    """

    def __init__(self) -> None:
        self.markitdown = MarkItDown()
        self.supported_extensions = [".pdf", ".docx", ".pptx", ".xlsx", ".xls"]
        self.text_extensions = [".md", ".txt"]

    def _get_file_extension(self, file_path: str) -> str:
        """
        Get the file extension in lowercase.
        Args:
            file_path (str): The file path.
        Returns:
            str: The file extension in lowercase.
        """
        return os.path.splitext(file_path)[1].lower()

    def _convert_single_file(self, file_path: str) -> str:
        """
        Convert a single file to markdown format.
        Args:
            file_path (str): The file path.
        Returns:
            str: The markdown content of the file.
        """
        extension = self._get_file_extension(file_path)

        if extension in self.text_extensions:
            # For .md and .txt files, just read the content
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        elif extension in self.supported_extensions:
            # For supported file types, use markitdown
            try:
                result = self.markitdown.convert(file_path)
                return str(result.text_content)
            except Exception as e:
                raise ValueError(f"Error converting file {file_path}: {str(e)}")
        else:
            raise ValueError(f"Unsupported file extension: {extension}")

    @component.output_types(markdowns=List[str])
    def run(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Convert the provided files to markdown format.

        Args:
            file_paths (List[str]): The paths to the files to be converted.

        Returns:
            Dict[str, List[str]]: The converted files in markdown format.
        """
        markdowns: List[str] = []
        for file_path in file_paths:
            markdown_string = self._convert_single_file(file_path)
            markdowns.append(markdown_string)

        return {"markdowns": markdowns}

    @component.output_types(markdowns=List[str])
    async def run_async(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Convert the provided files to markdown format asynchronously.

        Args:
            file_paths (List[str]): The paths to the files to be converted.

        Returns:
            Dict[str, List[str]]: The converted files in markdown format.
        """
        if not file_paths:
            return {"markdowns": []}

        loop = asyncio.get_event_loop()

        # Create tasks for all file conversions
        tasks = [
            loop.run_in_executor(None, self._convert_single_file, file_path)
            for file_path in file_paths
        ]

        # Wait for all tasks to complete
        markdowns = await asyncio.gather(*tasks)

        return {"markdowns": markdowns}
