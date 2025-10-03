from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, status
from hayhooks import log

from src.schemas.document import BaseResponse, GetDocumentResponse, MonaDocument
from src.services.documents_service import DocumentManager

router = APIRouter(prefix="/documents", tags=["documents"])


@lru_cache()
def get_document_manager() -> DocumentManager:
    """
    Returns the shared document manager instance for dependencies.
    Uses lru_cache to ensure only one instance is created.
    """
    return DocumentManager()


@router.get(
    "/",
    response_model=GetDocumentResponse,
    status_code=200,
    summary="Get All Documents",
    description="Retrieve metadata for all documents with unique source_id. Returns a list of unique documents based on their source_id.",
    response_description="List of document metadata with status information",
)
async def get_all_documents(
    doc_manager: DocumentManager = Depends(get_document_manager),
) -> GetDocumentResponse:
    """
    Retrieve metadata for all documents with unique source_id.

    Returns a list of unique documents based on their source_id.
    """
    try:
        documents_metadata = await doc_manager.get_documents()
        return GetDocumentResponse(
            status_code=status.HTTP_200_OK,
            message=f"Successfully retrieved {len(documents_metadata)} documents",
            documents=documents_metadata,
        )

    except Exception as e:
        log.error("Failed to retrieve documents: {}", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {str(e)}",
        )


@router.put(
    "/{source_id}",
    response_model=BaseResponse,
    status_code=200,
    summary="Update Document Metadata",
    description="Update document metadata with automatic validation. Only non-null fields in the request body will be updated.",
    response_description="Confirmation of successful metadata update",
)
async def update_document_metadata(
    source_id: str,
    metadata_update: MonaDocument,
    doc_manager: DocumentManager = Depends(get_document_manager),
) -> BaseResponse:
    """Update document metadata with automatic validation."""
    try:
        metadata = metadata_update.get_update_fields()
        success = await doc_manager.update_document_metadata(source_id, metadata)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with source_id '{source_id}' not found",
            )

        return BaseResponse(
            status_code=status.HTTP_200_OK,
            message="Document metadata updated successfully",
        )

    except HTTPException:
        raise  # Re-raise HTTPException without catching
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        log.error("Failed to update metadata for source_id {}: {}", source_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update document metadata: {str(e)}",
        )


@router.delete(
    "/{source_id}",
    response_model=BaseResponse,
    status_code=200,
    summary="Delete Document",
    description="Delete all chunks belonging to an original document by source_id. This will permanently remove the document and all its associated chunks from the system.",
    response_description="Confirmation of successful document deletion",
)
async def delete_document(
    source_id: str, doc_manager: DocumentManager = Depends(get_document_manager)
) -> BaseResponse:
    """
    Delete all chunks belonging to an original document by source_id.

    Args:
        source_id: The source_id of the original document to delete
    """
    try:
        deleted_count = await doc_manager.delete_document_by_source_id(source_id)

        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with source_id '{source_id}' not found",
            )

        return BaseResponse(
            status_code=status.HTTP_200_OK,
            message="Successfully deleted document.",
        )
    except ValueError as e:
        log.warning("Invalid source_id provided: {}", source_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log.error("Failed to delete document with source_id {}: {}", source_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}",
        )


@router.get(
    "/health",
    response_model=BaseResponse,
    status_code=200,
    summary="Documents Service Health Check",
    description="Check health of documents service. Used to verify that the documents service is operational and ready to handle requests.",
    response_description="Health status confirmation for the documents service",
)
async def health_check() -> BaseResponse:
    """Health check endpoint for the documents service."""
    return BaseResponse(
        status_code=status.HTTP_200_OK,
        message="Documents service is healthy",
    )
