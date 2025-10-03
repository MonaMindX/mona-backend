"""
Document Service contains the logic for managing documents in the Mona application.
"""

from typing import Any, Dict, List

from hayhooks import log
from haystack import Document
from haystack.document_stores.types import DuplicatePolicy
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore

from src.config.settings import document_store
from src.schemas.document import MonaDocument


class DocumentManager:
    """
    Service class for managing documents in the Mona application.

    This class provides a high-level interface for document operations including
    listing, retrieving, updating, and deleting documents from the PgVector document store.

    Note: In Haystack, documents are split into chunks during preprocessing, so each
    chunk becomes a separate document with the same source_id but different split_id.

    Attributes:
        document_store (PgvectorDocumentStore): The underlying document store instance.
    """

    def __init__(self, document_store: PgvectorDocumentStore = document_store):
        """
        Initialize the DocumentManager with a document store.

        Args:
            document_store (PgvectorDocumentStore): The document store to use for operations.

        Raises:
            ValueError: If document_store is None.
        """

        self.document_store = document_store

        log.debug("DocumentManager initialized successfully")

    async def get_documents(self) -> List[MonaDocument]:
        """
        Retrieve metadata for all documents with unique source_id.
        Returns:
            List[MonaDocument]: List of metadata dicts with unique source_id.
        Raises:
            RuntimeError: If document retrieval fails.
        """
        try:
            log.debug("Retrieving all documents")
            documents = await self.document_store.filter_documents_async()

            meta_by_source: Dict[str, Any] = {}
            for doc in documents:
                source_id = doc.meta.get("source_id")
                if source_id and source_id not in meta_by_source:
                    meta_by_source[source_id] = doc.meta

            unique_meta_list: List[MonaDocument] = list(meta_by_source.values())
            log.debug("Retrieved {} documents", len(unique_meta_list))
            return unique_meta_list

        except Exception as e:
            log.error("Failed to retrieve unique metadata: {}", e)
            raise RuntimeError(f"Failed to retrieve unique metadata: {e}") from e

    async def get_all_chunks_by_source_id(self, source_id: str) -> List[Document]:
        """
        Retrieve all chunks belonging to the same original document by source_id.

        Args:
            source_id (str): The source_id of the original document.

        Returns:
            List[Document]: List of all chunks from the same original document, sorted by split_id.

        Raises:
            ValueError: If source_id is empty or None.
            RuntimeError: If document retrieval fails.
        """
        if not source_id or not source_id.strip():
            raise ValueError("Source ID cannot be empty or None")

        try:
            log.debug("Retrieving all chunks for source_id: {}", source_id)

            chunks: List[Document] = await self.document_store.filter_documents_async(
                filters={
                    "field": "meta.source_id",
                    "operator": "==",
                    "value": source_id,
                }
            )

            log.debug("Retrieved {} chunks for source_id: {}", len(chunks), source_id)
            return chunks

        except Exception as e:
            log.error("Failed to retrieve chunks for source_id {}: {}", source_id, e)
            raise RuntimeError(f"Failed to retrieve document chunks: {e}") from e

    async def update_document_metadata(
        self, source_id: str, metadata: Dict[str, Any]
    ) -> bool:
        """
        Update the metadata of all chunks belonging to an original document.

        Args:
            source_id (str): The source_id of the original document.
            metadata (Dict[str, Any]): The metadata fields to update.

        Returns:
            bool: True if the document was successfully updated, False if document not found.

        Raises:
            ValueError: If source_id is empty or metadata is None.
            RuntimeError: If the update operation fails.
        """
        # Input validation
        if not source_id or not source_id.strip():
            raise ValueError("Source ID cannot be empty or None")

        try:
            log.debug(
                "Updating metadata for source_id: {} with data: {}", source_id, metadata
            )

            # Get all chunks for this source_id
            chunks = await self.get_all_chunks_by_source_id(source_id)
            if not chunks:
                log.warning(
                    "Cannot update metadata: no chunks found for source_id: {}",
                    source_id,
                )
                return False

            # Update metadata for all chunks
            updated_chunks: List[Document] = []
            for chunk in chunks:
                # Create a new document with updated metadata
                updated_meta = chunk.meta.copy()
                updated_meta.update(metadata)

                updated_chunk = Document(
                    id=chunk.id,
                    content=chunk.content,
                    meta=updated_meta,
                    embedding=chunk.embedding,
                )
                updated_chunks.append(updated_chunk)

            # Use write_documents with policy to overwrite existing documents
            await self.document_store.write_documents_async(
                updated_chunks, policy=DuplicatePolicy.OVERWRITE
            )

            log.debug(
                "Successfully updated metadata for {} chunks with source_id: {}",
                len(updated_chunks),
                source_id,
            )
            return True

        except Exception as e:
            log.error("Failed to update metadata for source_id {}: {}", source_id, e)
            raise RuntimeError(f"Failed to update document metadata: {e}") from e

    async def delete_document_by_source_id(self, source_id: str) -> int:
        """
        Delete all chunks belonging to an original document by source_id.

        Args:
            source_id (str): The source_id of the original document to delete.

        Returns:
            int: Number of chunks successfully deleted.

        Raises:
            ValueError: If source_id is empty or None.
            RuntimeError: If the deletion operation fails.
        """
        if not source_id or not source_id.strip():
            raise ValueError("Source ID cannot be empty or None")

        try:
            log.debug("Deleting all chunks for source_id: {}", source_id)

            # Get all chunk IDs for this source_id
            chunks = await self.get_all_chunks_by_source_id(source_id)
            if not chunks:
                log.warning(
                    "No chunks found for deletion with source_id: {}", source_id
                )
                return 0

            chunk_ids = [chunk.id for chunk in chunks]

            # Perform deletion
            await self.document_store.delete_documents_async(chunk_ids)

            log.debug(
                "Successfully deleted {} chunks for source_id: {}",
                len(chunk_ids),
                source_id,
            )
            return len(chunk_ids)

        except Exception as e:
            log.error("Failed to delete chunks for source_id {}: {}", source_id, e)
            raise RuntimeError(f"Failed to delete document chunks: {e}") from e
