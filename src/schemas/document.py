"""
Document schema definitions for the Mona knowledge base system.

This module provides Pydantic models and utility functions for representing
and validating documents within the Mona platform. Documents are the core
data structures used throughout the indexing pipeline and knowledge base
storage system.
"""

import uuid
from datetime import datetime
from typing import Dict, Optional, Union

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
        json_schema_extra: Dict[str, Dict[str, Union[str, int]]] = {
            "example": {
                "title": "Elden Ring Boss Strategy Guide",
                "summary": "Detailed strategies for all major boss encounters",
                "document_type": "guide",
                "file_name": "elden_ring_boss_guide.pdf",
                "file_size": 2048576,
                "created_at": "2022-01-01T12:00:00",
            }
        }
