from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock

import pytest
from haystack import Document
from haystack.document_stores.types import DuplicatePolicy

from src.services.documents_service import DocumentManager


@pytest.fixture
def mock_document_store() -> Any:
    """Create a mock PgvectorDocumentStore."""
    mock_store = MagicMock()
    mock_store.filter_documents_async = AsyncMock()
    mock_store.write_documents_async = AsyncMock()
    mock_store.delete_documents_async = AsyncMock()
    return mock_store


@pytest.fixture
def document_manager(mock_document_store: Any) -> Any:
    """Create a DocumentManager instance with mocked document store."""
    return DocumentManager(document_store=mock_document_store)


@pytest.fixture
def sample_documents() -> List[Document]:
    """Create sample Haystack documents for testing."""
    return [
        Document(
            id="chunk1",
            content="Content of chunk 1",
            meta={
                "source_id": "doc1",
                "split_id": 0,
                "title": "Document 1",
            },
            embedding=[0.1, 0.2, 0.3],
        ),
        Document(
            id="chunk2",
            content="Content of chunk 2",
            meta={
                "source_id": "doc1",
                "split_id": 1,
                "title": "Document 1",
            },
            embedding=[0.4, 0.5, 0.6],
        ),
        Document(
            id="chunk3",
            content="Content of chunk 3",
            meta={
                "source_id": "doc2",
                "split_id": 0,
                "title": "Document 2",
            },
            embedding=[0.7, 0.8, 0.9],
        ),
    ]


class TestDocumentManagerInit:
    """Test DocumentManager initialization."""

    def test_init_with_document_store(self, mock_document_store: Any) -> None:
        """Test successful initialization with a document store."""
        manager = DocumentManager(document_store=mock_document_store)
        assert manager.document_store == mock_document_store


class TestGetDocuments:
    """Test get_documents method."""

    @pytest.mark.asyncio
    async def test_get_documents_success(
        self, document_manager: Any, mock_document_store: Any, sample_documents: Any
    ) -> None:
        """Test successful retrieval of unique documents."""
        mock_document_store.filter_documents_async.return_value = sample_documents

        result = await document_manager.get_documents()

        assert len(result) == 2  # Two unique source_ids
        mock_document_store.filter_documents_async.assert_awaited_once()

        # Verify unique source_ids
        source_ids = [doc["source_id"] for doc in result]
        assert "doc1" in source_ids
        assert "doc2" in source_ids

    @pytest.mark.asyncio
    async def test_get_documents_empty_store(
        self, document_manager: Any, mock_document_store: Any
    ) -> None:
        """Test retrieval when document store is empty."""
        mock_document_store.filter_documents_async.return_value = []

        result = await document_manager.get_documents()

        assert result == []
        mock_document_store.filter_documents_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_documents_with_missing_source_id(
        self, document_manager: Any, mock_document_store: Any
    ) -> None:
        """Test retrieval with documents missing source_id."""
        documents_with_missing_id = [
            Document(
                id="chunk1",
                content="Content",
                meta={"source_id": "doc1", "title": "Doc 1"},
            ),
            Document(
                id="chunk2",
                content="Content",
                meta={"title": "Doc without source_id"},  # Missing source_id
            ),
            Document(
                id="chunk3",
                content="Content",
                meta={"source_id": None, "title": "Doc with None source_id"},
            ),
        ]
        mock_document_store.filter_documents_async.return_value = (
            documents_with_missing_id
        )

        result = await document_manager.get_documents()

        # Only doc1 should be included
        assert len(result) == 1
        assert result[0]["source_id"] == "doc1"

    @pytest.mark.asyncio
    async def test_get_documents_exception(
        self, document_manager: Any, mock_document_store: Any
    ) -> None:
        """Test exception handling during document retrieval."""
        mock_document_store.filter_documents_async.side_effect = Exception(
            "Database error"
        )

        with pytest.raises(RuntimeError) as exc_info:
            await document_manager.get_documents()

        assert "Failed to retrieve unique metadata" in str(exc_info.value)
        assert "Database error" in str(exc_info.value)


class TestGetAllChunksBySourceId:
    """Test get_all_chunks_by_source_id method."""

    @pytest.mark.asyncio
    async def test_get_chunks_success(
        self, document_manager: Any, mock_document_store: Any, sample_documents: Any
    ) -> None:
        """Test successful retrieval of chunks by source_id."""
        chunks_for_doc1 = [
            doc for doc in sample_documents if doc.meta["source_id"] == "doc1"
        ]
        mock_document_store.filter_documents_async.return_value = chunks_for_doc1

        result = await document_manager.get_all_chunks_by_source_id("doc1")

        assert len(result) == 2
        assert all(chunk.meta["source_id"] == "doc1" for chunk in result)
        mock_document_store.filter_documents_async.assert_awaited_once_with(
            filters={
                "field": "meta.source_id",
                "operator": "==",
                "value": "doc1",
            }
        )

    @pytest.mark.asyncio
    async def test_get_chunks_empty_source_id(self, document_manager: Any) -> None:
        """Test with empty source_id."""
        with pytest.raises(ValueError) as exc_info:
            await document_manager.get_all_chunks_by_source_id("")

        assert "Source ID cannot be empty or None" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_chunks_whitespace_source_id(self, document_manager: Any) -> None:
        """Test with whitespace-only source_id."""
        with pytest.raises(ValueError) as exc_info:
            await document_manager.get_all_chunks_by_source_id("   ")

        assert "Source ID cannot be empty or None" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_chunks_none_source_id(self, document_manager: Any) -> None:
        """Test with None source_id."""
        with pytest.raises(ValueError) as exc_info:
            await document_manager.get_all_chunks_by_source_id(None)

        assert "Source ID cannot be empty or None" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_chunks_no_results(
        self, document_manager: Any, mock_document_store: Any
    ) -> None:
        """Test when no chunks are found for source_id."""
        mock_document_store.filter_documents_async.return_value = []

        result = await document_manager.get_all_chunks_by_source_id("nonexistent")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_chunks_exception(
        self, document_manager: Any, mock_document_store: Any
    ) -> None:
        """Test exception handling during chunk retrieval."""
        mock_document_store.filter_documents_async.side_effect = Exception(
            "Query failed"
        )

        with pytest.raises(RuntimeError) as exc_info:
            await document_manager.get_all_chunks_by_source_id("doc1")

        assert "Failed to retrieve document chunks" in str(exc_info.value)
        assert "Query failed" in str(exc_info.value)


class TestUpdateDocumentMetadata:
    """Test update_document_metadata method."""

    @pytest.mark.asyncio
    async def test_update_metadata_success(
        self, document_manager: Any, mock_document_store: Any, sample_documents: Any
    ) -> None:
        """Test successful metadata update."""
        chunks_for_doc1 = [
            doc for doc in sample_documents if doc.meta["source_id"] == "doc1"
        ]
        mock_document_store.filter_documents_async.return_value = chunks_for_doc1

        metadata_update = {"title": "Updated Title"}
        result = await document_manager.update_document_metadata(
            "doc1", metadata_update
        )

        assert result is True
        mock_document_store.write_documents_async.assert_awaited_once()

        # Verify the call arguments
        call_args = mock_document_store.write_documents_async.call_args
        updated_docs = call_args[0][0]
        policy = call_args[1]["policy"]

        assert len(updated_docs) == 2
        assert policy == DuplicatePolicy.OVERWRITE
        assert all(doc.meta["title"] == "Updated Title" for doc in updated_docs)

    @pytest.mark.asyncio
    async def test_update_metadata_empty_source_id(self, document_manager: Any) -> None:
        """Test update with empty source_id."""
        with pytest.raises(ValueError) as exc_info:
            await document_manager.update_document_metadata("", {"title": "New Title"})

        assert "Source ID cannot be empty or None" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_metadata_whitespace_source_id(
        self, document_manager: Any
    ) -> None:
        """Test update with whitespace-only source_id."""
        with pytest.raises(ValueError) as exc_info:
            await document_manager.update_document_metadata(
                "   ", {"title": "New Title"}
            )

        assert "Source ID cannot be empty or None" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_metadata_document_not_found(
        self, document_manager: Any, mock_document_store: Any
    ) -> None:
        """Test update when document is not found."""
        mock_document_store.filter_documents_async.return_value = []

        result = await document_manager.update_document_metadata(
            "nonexistent", {"title": "New Title"}
        )

        assert result is False
        mock_document_store.write_documents_async.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_metadata_preserves_existing_fields(
        self, document_manager: Any, mock_document_store: Any, sample_documents: Any
    ) -> None:
        """Test that update preserves existing metadata fields."""
        chunks_for_doc1 = [
            doc for doc in sample_documents if doc.meta["source_id"] == "doc1"
        ]
        mock_document_store.filter_documents_async.return_value = chunks_for_doc1

        metadata_update = {"title": "Updated Title"}
        await document_manager.update_document_metadata("doc1", metadata_update)

        call_args = mock_document_store.write_documents_async.call_args
        updated_docs = call_args[0][0]

        # Verify that existing fields are preserved
        for doc in updated_docs:
            assert doc.meta["title"] == "Updated Title"
            assert doc.meta["source_id"] == "doc1"  # Original source_id preserved
            assert "split_id" in doc.meta  # Original split_id preserved

    @pytest.mark.asyncio
    async def test_update_metadata_preserves_content_and_embedding(
        self, document_manager: Any, mock_document_store: Any, sample_documents: Any
    ) -> None:
        """Test that update preserves document content and embeddings."""
        chunks_for_doc1 = [
            doc for doc in sample_documents if doc.meta["source_id"] == "doc1"
        ]
        mock_document_store.filter_documents_async.return_value = chunks_for_doc1

        metadata_update = {"title": "Updated Title"}
        await document_manager.update_document_metadata("doc1", metadata_update)

        call_args = mock_document_store.write_documents_async.call_args
        updated_docs = call_args[0][0]

        # Verify content and embeddings are preserved
        assert updated_docs[0].content == "Content of chunk 1"
        assert updated_docs[1].content == "Content of chunk 2"
        assert updated_docs[0].embedding == [0.1, 0.2, 0.3]
        assert updated_docs[1].embedding == [0.4, 0.5, 0.6]

    @pytest.mark.asyncio
    async def test_update_metadata_multiple_fields(
        self, document_manager: Any, mock_document_store: Any, sample_documents: Any
    ) -> None:
        """Test updating multiple metadata fields at once."""
        chunks_for_doc1 = [
            doc for doc in sample_documents if doc.meta["source_id"] == "doc1"
        ]
        mock_document_store.filter_documents_async.return_value = chunks_for_doc1

        metadata_update: Dict[str, Any] = {
            "title": "New Title",
            "category": "New Category",
            "tags": ["tag1", "tag2"],
        }
        result = await document_manager.update_document_metadata(
            "doc1", metadata_update
        )

        assert result is True
        call_args = mock_document_store.write_documents_async.call_args
        updated_docs = call_args[0][0]

        for doc in updated_docs:
            assert doc.meta["title"] == "New Title"
            assert doc.meta["category"] == "New Category"
            assert doc.meta["tags"] == ["tag1", "tag2"]

    @pytest.mark.asyncio
    async def test_update_metadata_exception_during_write(
        self, document_manager: Any, mock_document_store: Any, sample_documents: Any
    ) -> None:
        """Test exception handling when write operation fails."""
        chunks_for_doc1 = [
            doc for doc in sample_documents if doc.meta["source_id"] == "doc1"
        ]
        mock_document_store.filter_documents_async.return_value = chunks_for_doc1
        mock_document_store.write_documents_async.side_effect = Exception(
            "Write failed"
        )

        with pytest.raises(RuntimeError) as exc_info:
            await document_manager.update_document_metadata(
                "doc1", {"title": "New Title"}
            )

        assert "Failed to update document metadata" in str(exc_info.value)
        assert "Write failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_metadata_exception_during_retrieval(
        self, document_manager: Any, mock_document_store: Any
    ) -> None:
        """Test exception handling when chunk retrieval fails during update."""
        mock_document_store.filter_documents_async.side_effect = Exception(
            "Retrieval failed"
        )

        with pytest.raises(RuntimeError) as exc_info:
            await document_manager.update_document_metadata(
                "doc1", {"title": "New Title"}
            )

        assert "Failed to update document metadata" in str(exc_info.value)


class TestDeleteDocumentBySourceId:
    """Test delete_document_by_source_id method."""

    @pytest.mark.asyncio
    async def test_delete_document_success(
        self, document_manager: Any, mock_document_store: Any, sample_documents: Any
    ) -> None:
        """Test successful deletion of all chunks for a document."""
        chunks_for_doc1 = [
            doc for doc in sample_documents if doc.meta["source_id"] == "doc1"
        ]
        mock_document_store.filter_documents_async.return_value = chunks_for_doc1

        result = await document_manager.delete_document_by_source_id("doc1")

        assert result == 2  # Two chunks deleted
        mock_document_store.delete_documents_async.assert_awaited_once_with(
            ["chunk1", "chunk2"]
        )

    @pytest.mark.asyncio
    async def test_delete_document_empty_source_id(self, document_manager: Any) -> None:
        """Test deletion with empty source_id."""
        with pytest.raises(ValueError) as exc_info:
            await document_manager.delete_document_by_source_id("")

        assert "Source ID cannot be empty or None" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_document_whitespace_source_id(
        self, document_manager: Any
    ) -> None:
        """Test deletion with whitespace-only source_id."""
        with pytest.raises(ValueError) as exc_info:
            await document_manager.delete_document_by_source_id("   ")

        assert "Source ID cannot be empty or None" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_document_none_source_id(self, document_manager: Any) -> None:
        """Test deletion with None source_id."""
        with pytest.raises(ValueError) as exc_info:
            await document_manager.delete_document_by_source_id(None)

        assert "Source ID cannot be empty or None" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_document_not_found(
        self, document_manager: Any, mock_document_store: Any
    ) -> None:
        """Test deletion when document is not found."""
        mock_document_store.filter_documents_async.return_value = []

        result = await document_manager.delete_document_by_source_id("nonexistent")

        assert result == 0
        mock_document_store.delete_documents_async.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_delete_document_single_chunk(
        self, document_manager: Any, mock_document_store: Any
    ) -> None:
        """Test deletion of document with single chunk."""
        single_chunk = [
            Document(
                id="chunk1",
                content="Content",
                meta={"source_id": "doc1", "split_id": 0},
            )
        ]
        mock_document_store.filter_documents_async.return_value = single_chunk

        result = await document_manager.delete_document_by_source_id("doc1")

        assert result == 1
        mock_document_store.delete_documents_async.assert_awaited_once_with(["chunk1"])

    @pytest.mark.asyncio
    async def test_delete_document_multiple_chunks(
        self, document_manager: Any, mock_document_store: Any
    ) -> None:
        """Test deletion of document with many chunks."""
        many_chunks = [
            Document(
                id=f"chunk{i}",
                content=f"Content {i}",
                meta={"source_id": "doc1", "split_id": i},
            )
            for i in range(10)
        ]
        mock_document_store.filter_documents_async.return_value = many_chunks

        result = await document_manager.delete_document_by_source_id("doc1")

        assert result == 10
        call_args = mock_document_store.delete_documents_async.call_args
        deleted_ids = call_args[0][0]
        assert len(deleted_ids) == 10
        assert all(f"chunk{i}" in deleted_ids for i in range(10))

    @pytest.mark.asyncio
    async def test_delete_document_exception_during_retrieval(
        self, document_manager: Any, mock_document_store: Any
    ) -> None:
        """Test exception handling when chunk retrieval fails during deletion."""
        mock_document_store.filter_documents_async.side_effect = Exception(
            "Retrieval failed"
        )

        with pytest.raises(RuntimeError) as exc_info:
            await document_manager.delete_document_by_source_id("doc1")

        assert "Failed to delete document chunks" in str(exc_info.value)
        mock_document_store.delete_documents_async.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_delete_document_exception_during_deletion(
        self, document_manager: Any, mock_document_store: Any, sample_documents: Any
    ) -> None:
        """Test exception handling when deletion operation fails."""
        chunks_for_doc1 = [
            doc for doc in sample_documents if doc.meta["source_id"] == "doc1"
        ]
        mock_document_store.filter_documents_async.return_value = chunks_for_doc1
        mock_document_store.delete_documents_async.side_effect = Exception(
            "Deletion failed"
        )

        with pytest.raises(RuntimeError) as exc_info:
            await document_manager.delete_document_by_source_id("doc1")

        assert "Failed to delete document chunks" in str(exc_info.value)
        assert "Deletion failed" in str(exc_info.value)
