"""
Document schema definitions for the Mona knowledge base system.

This module provides Pydantic models and utility functions for representing
and validating documents within the Mona platform. Documents are the core
data structures used throughout the indexing pipeline and knowledge base
storage system.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


def iso_date_factory() -> str:
    """
    Factory function for creating ISO 8601-formatted date strings.
    """
    return datetime.now().isoformat()


def uuid4_factory() -> str:
    """
    Factory function for creating UUID4 strings.
    """
    return str(uuid.uuid4())


class MonaDocument(BaseModel):
    """
    Represents a document in the Mona knowledge base.

    This model is used for storing and retrieving documents
    that can be indexed and searched through the Mona system.
    """

    source_id: str = Field(
        default_factory=uuid4_factory,
        description="Unique identifier for the source document",
    )

    title: Optional[str] = Field(
        default=None,
        description="The title or name of the document",
        min_length=1,
        max_length=255,
    )

    summary: Optional[str] = Field(
        default=None,
        description="A brief summary or description of the document content",
        max_length=500,
    )

    document_type: Optional[str] = Field(
        default=None,
        description="Type of document (e.g., 'guide', 'walkthrough', 'tips', 'review')",
        max_length=50,
    )

    file_name: Optional[str] = Field(
        default=None,
        description="The original filename of the uploaded document",
        min_length=1,
        max_length=255,
    )

    file_size: Optional[int] = Field(
        default=None, description="Size of the original file in bytes", ge=0
    )

    created_at: str = Field(
        default_factory=iso_date_factory,
        description="Timestamp when the document was created (ISO format)",
    )

    class ConfigDict:
        json_schema_extra: Dict[str, Any] = {
            "example": {
                "title": "Elden Ring Boss Strategy Guide",
                "summary": "Detailed strategies for all major boss encounters",
                "document_type": "guide",
                "file_name": "elden_ring_boss_guide.pdf",
                "file_size": 2048576,
                "created_at": "2022-01-01T12:00:00",
            }
        }

    def get_update_fields(self) -> Dict[str, Any]:
        """
        Extract non-None fields for updating document metadata.

        Returns:
            Dict containing only the fields that are not None

        Raises:
            ValueError: If no fields are provided for update
        """
        # Get all fields except source_id and created_at (these shouldn't be updated)
        updatable_fields: Dict[str, Any] = {
            "title": self.title,
            "summary": self.summary,
            "document_type": self.document_type,
            "file_name": self.file_name,
            "file_size": self.file_size,
        }

        # Filter out None values
        update_data = {k: v for k, v in updatable_fields.items() if v is not None}

        if not update_data:
            raise ValueError("At least one field must be provided for update")

        return update_data


class BaseResponse(BaseModel):
    """Base response model for the Document API."""

    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Response message")
    timestamp: str = Field(
        default_factory=iso_date_factory, description="Timestamp of the response"
    )


class GetDocumentResponse(BaseResponse):
    """Response model for the document details."""

    documents: List[MonaDocument] = Field(..., description="List of documents")

    class ConfigDict:
        json_schema_extra: Dict[str, Any] = {
            "example": {
                "documents": [
                    {
                        "title": "Elden Ring Boss Strategy Guide",
                        "summary": "Detailed strategies for all major boss encounters",
                        "document_type": "guide",
                        "file_name": "elden_ring_boss_guide.pdf",
                        "file_size": 2048576,
                        "created_at": "2022-01-01T12:00:00",
                    }
                ],
                "status_code": 200,
                "message": "OK",
                "timestamp": "2023-01-01T12:00:00",
            }
        }
