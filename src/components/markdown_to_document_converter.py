"""
The MarkdownToDocumentConverter converts markdown to a haystack document.
"""

import asyncio
from typing import Dict, List

from haystack import Document, component

from src.schemas.document import MonaDocument


@component
class MarkdownToDocumentConverter:
    """
    Convert markdown(s) to haystack document(s).
    """

    @component.output_types(documents=List[Document])
    def run(
        self, markdowns: List[str], metadata: List[MonaDocument]
    ) -> Dict[str, List[Document]]:
        """
        Convert the provided markdowns to haystack documents.

        Args:
            markdowns (List[str]): The markdown contents to be converted.
            metadata (List[MonaDocument]): Metadata for each document.

        Returns:
            Dict[str, List[Document]]: Haystack documents containing the converted content.
        """
        if len(markdowns) != len(metadata):
            raise ValueError(
                f"Number of markdowns ({len(markdowns)}) must match number of metadata items ({len(metadata)})"
            )

        documents: List[Document] = []
        for markdown, meta in zip(markdowns, metadata):
            document = Document(content=markdown, meta=meta.model_dump())
            documents.append(document)

        return {"documents": documents}

    @component.output_types(documents=List[Document])
    async def run_async(
        self, markdowns: List[str], metadata: List[MonaDocument]
    ) -> Dict[str, List[Document]]:
        """
        Convert the provided markdowns to haystack documents asynchronously.

        Args:
            markdowns (List[str]): The markdown contents to be converted.
            metadata (List[MonaDocument]): Metadata for each document.

        Returns:
            Dict[str, List[Document]]: Haystack documents containing the converted content.
        """
        if len(markdowns) != len(metadata):
            raise ValueError(
                f"Number of markdowns ({len(markdowns)}) must match number of metadata items ({len(metadata)})"
            )

        if not markdowns:
            return {"documents": []}

        loop = asyncio.get_event_loop()

        # Create tasks for all document conversions
        async def create_document(markdown: str, meta: MonaDocument) -> Document:
            return await loop.run_in_executor(
                None, lambda: Document(content=markdown, meta=meta.model_dump())
            )

        # Process all markdowns concurrently
        documents = await asyncio.gather(
            *[
                create_document(markdown, meta)
                for markdown, meta in zip(markdowns, metadata)
            ]
        )

        return {"documents": documents}
