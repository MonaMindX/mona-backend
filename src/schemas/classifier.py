"""
Enhanced classifier schema with proper typing and validation.

This module provides comprehensive Pydantic models for the classifier component,
including proper validation, field constraints, and type safety.
"""

from enum import Enum
from typing import Any, Dict, List, Set

from pydantic import BaseModel, ConfigDict, Field


class QueryType(str, Enum):
    """Query classification types for routing decisions."""

    DOCUMENT_RETRIEVAL = "document_retrieval"
    CONVERSATIONAL = "conversational"


class RuleType(str, Enum):
    """Types of classification rules available."""

    KEYWORD = "keyword"
    REGEX = "regex"
    PHRASE = "phrase"


class ClassificationRule(BaseModel):
    """
    Individual classification rule with pattern matching and scoring.

    Used to define specific patterns that indicate document retrieval
    or conversational intent in user queries.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    pattern: str = Field(
        ...,
        min_length=1,
        description="Pattern string for matching (keyword, phrase, or regex)",
    )
    rule_type: RuleType = Field(..., description="Type of matching rule to apply")
    weight: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Weight of rule impact on final score (0.0-1.0)",
    )
    category: QueryType = Field(
        ..., description="Classification category this rule supports"
    )
    description: str = Field(
        ..., min_length=1, description="Human-readable description of the rule purpose"
    )


class FeatureScores(BaseModel):
    """
    Container for feature engineering scores and diagnostic information.

    Stores intermediate calculation results for transparency and debugging.
    """

    doc_score: float = Field(
        default=0.0,
        description="Aggregated score supporting document retrieval classification",
    )
    conv_score: float = Field(
        default=0.0,
        description="Aggregated score supporting conversational classification",
    )
    notes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Diagnostic notes and intermediate calculations",
    )


class DomainStats(BaseModel):
    """
    Domain-specific term frequency statistics for TF-IDF simulation.

    Maps terms to their frequency counts in the domain corpus.
    """

    term_frequencies: Dict[str, int] = Field(
        ..., description="Mapping of terms to their corpus frequency counts"
    )
    total_terms: int = Field(
        ..., gt=0, description="Total number of terms in the corpus"
    )


class ClassificationConfig(BaseModel):
    """
    Configuration parameters for the classification process.

    Allows tuning of classification behavior and thresholds.
    """

    confidence_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for classification",
    )
    max_expected_score: float = Field(
        default=6.5,
        gt=0.0,
        description="Maximum expected combined score for confidence calculation",
    )
    separation_weight: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Weight for score separation in confidence calculation",
    )
    strength_weight: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Weight for score strength in confidence calculation",
    )


class QueryClassificationResult(BaseModel):
    """
    Complete result of query classification analysis.

    Contains the final routing decision, confidence metrics, and detailed
    diagnostic information for transparency and debugging.
    """

    needs_retrieval: bool = Field(
        ..., description="Whether the query requires document retrieval"
    )
    classification: QueryType = Field(..., description="Final classification category")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Classification confidence score (0.0-1.0)"
    )
    feature_scores: Dict[str, Any] = Field(
        ..., description="Detailed feature analysis and diagnostic information"
    )
    processing_time_ms: float = Field(
        default=0.0, ge=0.0, description="Processing time in milliseconds"
    )


class StopWords(BaseModel):
    """
    Collection of stop words to filter from query analysis.

    Contains common words that don't contribute to classification decisions.
    """

    words: Set[str] = Field(
        ..., description="Set of stop words to exclude from analysis"
    )


# Type aliases for better code readability
ClassificationRules = List[ClassificationRule]
TermFrequencies = Dict[str, int]
FeatureNotes = Dict[str, Any]
