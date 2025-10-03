from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.routes.documents import get_document_manager, router
from src.schemas.document import MonaDocument


@pytest.fixture
def mock_document_manager() -> Any:
    """Create a mock DocumentManager with async methods."""
    mock = MagicMock()
    # Make all methods async mocks
    mock.get_documents = AsyncMock()
    mock.update_document_metadata = AsyncMock()
    mock.delete_document_by_source_id = AsyncMock()
    return mock


@pytest.fixture
def client(mock_document_manager: Any) -> Any:
    """Create a test client with mocked dependencies."""
    app = FastAPI()
    app.include_router(router)

    # Override the dependency
    app.dependency_overrides[get_document_manager] = lambda: mock_document_manager

    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_get_all_documents_success(
    client: Any, mock_document_manager: Any
) -> None:
    """Test successful retrieval of all documents."""
    # Arrange
    mock_documents: List[Dict[str, Any]] = [
        {
            "source_id": "doc1",
            "title": "Document 1",
            "summary": None,
            "document_type": None,
            "file_name": None,
            "file_size": None,
            "created_at": "2024-01-01T00:00:00",
        },
        {
            "source_id": "doc2",
            "title": "Document 2",
            "summary": None,
            "document_type": None,
            "file_name": None,
            "file_size": None,
            "created_at": "2024-01-01T00:00:00",
        },
    ]
    mock_document_manager.get_documents.return_value = mock_documents

    # Act
    response = client.get("/documents/")

    # Assert
    assert response.status_code == 200
    assert response.json()["status_code"] == 200
    assert response.json()["message"] == "Successfully retrieved 2 documents"
    assert response.json()["documents"] == mock_documents
    mock_document_manager.get_documents.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_documents_error_handling(
    client: Any, mock_document_manager: Any
) -> None:
    """Test error handling when document manager raises an exception."""
    # Arrange
    mock_document_manager.get_documents.side_effect = Exception(
        "Database connection failed"
    )

    # Act
    response = client.get("/documents/")

    # Assert
    assert response.status_code == 500
    assert "Failed to retrieve documents" in response.json()["detail"]
    mock_document_manager.get_documents.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_document_metadata_success(
    client: Any, mock_document_manager: Any
) -> None:
    """Test successful update of document metadata."""
    # Arrange
    source_id = "doc1"
    update_data = {"title": "Updated Title", "author": "Updated Author"}
    mock_document_manager.update_document_metadata.return_value = True

    # Act
    response = client.put(f"/documents/{source_id}", json=update_data)

    # Assert
    assert response.status_code == 200
    assert response.json()["status_code"] == 200
    assert response.json()["message"] == "Document metadata updated successfully"
    mock_document_manager.update_document_metadata.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_document_metadata_not_found(
    client: Any, mock_document_manager: Any
) -> None:
    """Test update returns 404 when document is not found."""
    # Arrange
    source_id = "non_existent_doc"
    update_data = {"title": "Updated Title", "author": "Updated Author"}
    mock_document_manager.update_document_metadata.return_value = False

    # Act
    response = client.put(f"/documents/{source_id}", json=update_data)

    # Assert
    assert response.status_code == 404
    assert (
        f"Document with source_id '{source_id}' not found" in response.json()["detail"]
    )
    mock_document_manager.update_document_metadata.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_document_metadata_invalid_values(
    client: Any, mock_document_manager: Any
) -> None:
    """Test update returns 400 when invalid metadata values are provided."""
    # Arrange
    source_id = "doc1"
    update_data = {"title": "Valid Title", "author": "Valid Author"}
    mock_document_manager.update_document_metadata.side_effect = ValueError(
        "Invalid metadata value"
    )

    # Act
    response = client.put(f"/documents/{source_id}", json=update_data)

    # Assert
    assert response.status_code == 400
    assert "Invalid metadata value" in response.json()["detail"]
    mock_document_manager.update_document_metadata.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_document_metadata_unexpected_error(
    client: Any, mock_document_manager: Any
) -> None:
    """Test update returns 500 when an unexpected exception occurs."""
    # Arrange
    source_id = "doc1"
    update_data = {"title": "Updated Title", "author": "Updated Author"}
    mock_document_manager.update_document_metadata.side_effect = Exception(
        "Unexpected database error"
    )

    # Act
    response = client.put(f"/documents/{source_id}", json=update_data)

    # Assert
    assert response.status_code == 500
    assert "Failed to update document metadata" in response.json()["detail"]
    mock_document_manager.update_document_metadata.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_document_not_found(
    client: Any, mock_document_manager: Any
) -> None:
    """Test delete document returns 404 when source_id doesn't exist."""
    # Arrange
    source_id = "non_existent_doc"
    mock_document_manager.delete_document_by_source_id.return_value = 0

    # Act
    response = client.delete(f"/documents/{source_id}")

    # Assert
    assert response.status_code == 404
    assert (
        response.json()["detail"] == f"Document with source_id '{source_id}' not found"
    )
    mock_document_manager.delete_document_by_source_id.assert_awaited_once_with(
        source_id
    )


@pytest.mark.asyncio
async def test_delete_document_success(client: Any, mock_document_manager: Any) -> None:
    """Test successful deletion of an existing document."""
    # Arrange
    source_id = "doc1"
    mock_document_manager.delete_document_by_source_id.return_value = (
        5  # deleted 5 chunks
    )

    # Act
    response = client.delete(f"/documents/{source_id}")

    # Assert
    assert response.status_code == 200
    assert response.json()["status_code"] == 200
    assert response.json()["message"] == "Successfully deleted document."
    mock_document_manager.delete_document_by_source_id.assert_awaited_once_with(
        source_id
    )


@pytest.mark.asyncio
async def test_delete_document_invalid_source_id_format(
    client: Any, mock_document_manager: Any
) -> None:
    """Test delete returns 400 when source_id format is invalid."""
    # Arrange
    source_id = "invalid_id"
    mock_document_manager.delete_document_by_source_id.side_effect = ValueError(
        "Invalid source_id format"
    )

    # Act
    response = client.delete(f"/documents/{source_id}")

    # Assert
    assert response.status_code == 400
    assert "Invalid source_id format" in response.json()["detail"]
    mock_document_manager.delete_document_by_source_id.assert_awaited_once_with(
        source_id
    )


@pytest.mark.asyncio
async def test_health_check_success(client: Any) -> None:
    """Test health check endpoint returns 200 status and healthy message."""
    # Act
    response = client.get("/documents/health")

    # Assert
    assert response.status_code == 200
    assert response.json()["status_code"] == 200
    assert response.json()["message"] == "Documents service is healthy"


# ============================================================================
# NEW TESTS TO COVER MISSING CODE PATHS
# ============================================================================


@pytest.mark.asyncio
async def test_delete_document_generic_exception_with_logging(
    client: Any, mock_document_manager: Any
) -> None:
    """
    Test delete document handles generic exceptions and logs them properly.
    Covers: except Exception as e: log.error(...) raise HTTPException(500)
    """
    # Arrange
    source_id = "doc1"
    error_message = "Database connection timeout"
    mock_document_manager.delete_document_by_source_id.side_effect = RuntimeError(
        error_message
    )

    # Act
    with patch("src.routes.documents.log") as mock_log:
        response = client.delete(f"/documents/{source_id}")

        # Assert
        assert response.status_code == 500
        assert "Failed to delete document" in response.json()["detail"]
        assert error_message in response.json()["detail"]

        # Verify logging was called
        mock_log.error.assert_called_once()
        log_call_args = mock_log.error.call_args[0]
        assert "Failed to delete document with source_id" in log_call_args[0]
        assert source_id in str(log_call_args[1])


@pytest.mark.asyncio
async def test_delete_document_preserves_http_exceptions(
    client: Any, mock_document_manager: Any
) -> None:
    """
    Test that HTTPExceptions raised by the service are re-raised without modification.
    Covers: except HTTPException: raise
    """
    # Arrange
    source_id = "doc1"
    original_http_exception = HTTPException(
        status_code=403, detail="Permission denied for this operation"
    )
    mock_document_manager.delete_document_by_source_id.side_effect = (
        original_http_exception
    )

    # Act
    response = client.delete(f"/documents/{source_id}")

    # Assert - The original HTTPException should be preserved
    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied for this operation"


@pytest.mark.asyncio
async def test_delete_document_network_error(
    client: Any, mock_document_manager: Any
) -> None:
    """Test delete document handles network-related errors."""
    # Arrange
    source_id = "doc1"
    mock_document_manager.delete_document_by_source_id.side_effect = ConnectionError(
        "Network unreachable"
    )

    # Act
    response = client.delete(f"/documents/{source_id}")

    # Assert
    assert response.status_code == 500
    assert "Failed to delete document" in response.json()["detail"]
    assert "Network unreachable" in response.json()["detail"]


def test_get_document_manager_returns_instance() -> None:
    """
    Test that get_document_manager returns a DocumentManager instance.
    Covers: return DocumentManager()
    """
    # Act
    manager = get_document_manager()

    # Assert
    from src.services.documents_service import DocumentManager

    assert isinstance(manager, DocumentManager)
    assert manager is not None


def test_get_document_manager_caching() -> None:
    """Test that get_document_manager uses lru_cache correctly."""
    # Act
    manager1 = get_document_manager()
    manager2 = get_document_manager()

    # Assert - Should return the same instance due to lru_cache
    assert manager1 is manager2


def test_get_document_manager_cache_info() -> None:
    """Test that lru_cache is working by checking cache info."""
    # Clear cache first
    get_document_manager.cache_clear()

    # Act
    _ = get_document_manager()
    _ = get_document_manager()
    cache_info = get_document_manager.cache_info()

    # Assert
    assert cache_info.hits >= 1  # Second call should be a cache hit
    assert cache_info.misses >= 1  # First call should be a cache miss


@pytest.mark.asyncio
async def test_update_document_no_fields_provided_via_schema(
    client: Any, mock_document_manager: Any
) -> None:
    """
    Test that ValueError is raised when no update fields are provided.
    Covers: if not update_data: raise ValueError("At least one field must be provided for update")
    """
    # Arrange
    source_id = "doc1"
    # All fields are None - this should trigger the ValueError in get_update_fields()
    update_data: Dict[str, Any] = {
        "source_id": source_id,
        "title": None,
        "summary": None,
        "document_type": None,
        "file_name": None,
        "file_size": None,
    }

    # Act
    response = client.put(f"/documents/{source_id}", json=update_data)

    # Assert
    assert response.status_code == 400
    assert "At least one field must be provided for update" in response.json()["detail"]


def test_mona_document_get_update_fields_all_none() -> None:
    """
    Test MonaDocument.get_update_fields raises ValueError when all fields are None.
    Direct unit test for the schema method.
    """
    # Arrange
    document = MonaDocument(
        source_id="test-id",
        title=None,
        summary=None,
        document_type=None,
        file_name=None,
        file_size=None,
    )

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        document.get_update_fields()

    assert "At least one field must be provided for update" in str(exc_info.value)


def test_mona_document_get_update_fields_single_field() -> None:
    """Test get_update_fields with a single non-None field."""
    # Arrange
    document = MonaDocument(
        source_id="test-id",
        title="Updated Title",
        summary=None,
        document_type=None,
        file_name=None,
        file_size=None,
    )

    # Act
    update_fields = document.get_update_fields()

    # Assert
    assert update_fields == {"title": "Updated Title"}
    assert "source_id" not in update_fields
    assert "created_at" not in update_fields


def test_mona_document_get_update_fields_multiple_fields() -> None:
    """Test get_update_fields with multiple non-None fields."""
    # Arrange
    document = MonaDocument(
        source_id="test-id",
        title="Updated Title",
        summary="Updated Summary",
        document_type="PDF",
        file_name="updated_file.pdf",
        file_size=1024,
    )

    # Act
    update_fields = document.get_update_fields()

    # Assert
    expected: Dict[str, Any] = {
        "title": "Updated Title",
        "summary": "Updated Summary",
        "document_type": "PDF",
        "file_name": "updated_file.pdf",
        "file_size": 1024,
    }
    assert update_fields == expected
    assert "source_id" not in update_fields
    assert "created_at" not in update_fields
