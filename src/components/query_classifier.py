"""
IntegratedQueryClassifier: Comprehensive Query Classification Component

This component provides high-accuracy intent classification for queries in a RAG pipeline,
using advanced pattern recognition, linguistic feature engineering, and weighted decision logic.
The system is LLM-free and designed for fast, interpretable routing with comprehensive validation.
"""

import math
import re
import string
import time
from typing import Any, Dict, List, Optional

from haystack import component
from pydantic import ValidationError

from src.schemas.classifier import (
    ClassificationConfig,
    ClassificationRule,
    ClassificationRules,
    DomainStats,
    FeatureScores,
    QueryClassificationResult,
    QueryType,
    RuleType,
    StopWords,
    TermFrequencies,
)


@component
class IntegratedQueryClassifier:
    """
    High-performance integrated classifier for query intent detection.

    Features:
    - Multi-layer pattern recognition (keywords, phrases, regex)
    - Feature engineering (TF-IDF simulation, n-grams, POS simulation)
    - Weighted ensemble decision making with confidence scoring
    - Comprehensive validation and error handling
    - Performance monitoring and diagnostics
    """

    def __init__(self, config: Optional[ClassificationConfig] = None) -> None:
        """
        Initialize the classifier with rules, domain statistics, and configuration.

        Args:
            config: Optional classification configuration. Uses defaults if not provided.
        """
        self.config = config or ClassificationConfig()
        self.rules: ClassificationRules = self._build_rules()
        self.domain_stats: DomainStats = self._build_domain_stats()
        self.stop_words: StopWords = self._build_stop_words()

    def _build_rules(self) -> ClassificationRules:
        """Build comprehensive classification rules with proper validation."""
        rules: ClassificationRules = []

        # Document retrieval patterns
        doc_terms = [
            "document",
            "file",
            "pdf",
            "report",
            "policy",
            "procedure",
            "specification",
            "manual",
            "guide",
            "regulation",
            "compliance",
            "workflow",
            "protocol",
            "standard",
            "requirement",
            "documentation",
            "docs",
        ]

        info_patterns = [
            "what does",
            "how does",
            "where can",
            "show me",
            "find me",
            "search for",
            "look up",
            "according to",
            "based on",
            "mentioned in",
            "specified in",
            "outlined in",
            "detailed in",
            "described in",
            "defined in",
        ]

        compliance_terms = [
            "regulation",
            "requirement",
            "guideline",
            "protocol",
            "compliance",
        ]

        # Conversational patterns
        greeting_patterns = [
            r"^(hi|hello|hey|good\s+(morning|afternoon|evening))",
            r"\b(thanks?|thank\s+you)\b",
            r"\b(bye|goodbye|see\s+you|farewell)\b",
            r"^(how\s+are\s+you|how\'s\s+it\s+going|what\'s\s+up)\b",
        ]

        personal_phrases = [
            "i think",
            "i believe",
            "i feel",
            "in my opinion",
            "personally",
            "i like",
            "i prefer",
            "i want",
            "i need",
            "can you help",
            "could you",
            "would you",
            "please help",
        ]

        general_knowledge = [
            "tell me about",
            "explain",
            "what's the difference between",
            "compare",
            "why do",
            "fun fact",
            "famous",
            "popular",
            "best",
            "worst",
            "recommend",
        ]

        # Build validated rules
        try:
            # Document retrieval rules
            for term in doc_terms + compliance_terms:
                rules.append(
                    ClassificationRule(
                        pattern=term,
                        rule_type=RuleType.KEYWORD,
                        weight=0.9,
                        category=QueryType.DOCUMENT_RETRIEVAL,
                        description=f"Document-related term: {term}",
                    )
                )

            for pattern in info_patterns:
                rules.append(
                    ClassificationRule(
                        pattern=pattern,
                        rule_type=RuleType.PHRASE,
                        weight=0.7,
                        category=QueryType.DOCUMENT_RETRIEVAL,
                        description=f"Information-seeking pattern: {pattern}",
                    )
                )

            # Procedural regex rule
            rules.append(
                ClassificationRule(
                    pattern=r"\b(step\s+\d+|section\s+\d+|page\s+\d+|chapter\s+\d+)\b",
                    rule_type=RuleType.REGEX,
                    weight=0.8,
                    category=QueryType.DOCUMENT_RETRIEVAL,
                    description="Procedural reference pattern",
                )
            )

            # Conversational rules
            for pattern in greeting_patterns:
                rules.append(
                    ClassificationRule(
                        pattern=pattern,
                        rule_type=RuleType.REGEX,
                        weight=0.95,
                        category=QueryType.CONVERSATIONAL,
                        description=f"Greeting pattern: {pattern}",
                    )
                )

            # Informal response pattern
            rules.append(
                ClassificationRule(
                    pattern=r"^(ok|okay|yes|no|sure|alright|got\s+it)$",
                    rule_type=RuleType.REGEX,
                    weight=0.95,
                    category=QueryType.CONVERSATIONAL,
                    description="Informal response pattern",
                )
            )

            for phrase in personal_phrases + general_knowledge:
                rules.append(
                    ClassificationRule(
                        pattern=phrase,
                        rule_type=RuleType.PHRASE,
                        weight=0.8,
                        category=QueryType.CONVERSATIONAL,
                        description=f"Personal/general phrase: {phrase}",
                    )
                )

        except ValidationError as e:
            raise ValueError(f"Failed to build classification rules: {e}")

        return rules

    def _build_domain_stats(self) -> DomainStats:
        """Build domain statistics for TF-IDF simulation."""
        term_frequencies: TermFrequencies = {
            # High frequency (conversational)
            "hello": 1000,
            "hi": 800,
            "thanks": 600,
            "please": 500,
            "how": 400,
            "what": 390,
            "where": 300,
            "when": 220,
            # Low frequency (domain-specific)
            "policy": 15,
            "document": 20,
            "workflow": 8,
            "manual": 9,
            "protocol": 4,
        }

        return DomainStats(
            term_frequencies=term_frequencies,
            total_terms=sum(term_frequencies.values()),
        )

    def _build_stop_words(self) -> StopWords:
        """Build stop words collection."""
        words = {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "for",
            "from",
            "has",
            "he",
            "in",
            "is",
            "it",
            "its",
            "of",
            "on",
            "that",
            "the",
            "to",
            "was",
            "were",
            "will",
            "with",
            "would",
        }

        return StopWords(words=words)

    def _preprocess_query(self, query: str) -> str:
        """Clean and normalize the input query."""

        processed = query.lower().strip()
        processed = re.sub(r"\s+", " ", processed)
        processed = re.sub(r"[^\w\s\.\?\!\-\']", " ", processed)
        return processed

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from the query."""
        words = query.split()
        return [w for w in words if w not in self.stop_words.words and len(w) > 2]

    def _calculate_feature_scores(self, query: str) -> FeatureScores:
        """Calculate feature engineering scores for the query."""
        doc_score: float = 0.0
        conv_score: float = 0.0
        notes: Dict[str, Any] = {}

        # TF-IDF-like scoring
        for term, freq in self.domain_stats.term_frequencies.items():
            if term in query:
                tf = query.count(term) / max(1, len(query.split()))
                idf = math.log((self.domain_stats.total_terms + 1) / (freq + 1))
                score = tf * idf

                if freq < 20:  # Low frequency = domain-specific
                    doc_score += score
                else:  # High frequency = conversational
                    conv_score += score

        notes["tfidf_doc"] = doc_score
        notes["tfidf_conv"] = conv_score

        # N-gram analysis
        words = query.split()
        bigrams = [" ".join(words[i : i + 2]) for i in range(len(words) - 1)]

        doc_bigrams = [
            bg for bg in bigrams if bg in ["according to", "based on", "mentioned in"]
        ]
        conv_bigrams = [
            bg for bg in bigrams if bg in ["thank you", "please help", "can you"]
        ]

        doc_score += 0.7 * len(doc_bigrams)
        conv_score += 0.5 * len(conv_bigrams)

        notes["bigrams_doc"] = doc_bigrams
        notes["bigrams_conv"] = conv_bigrams

        # Question word and structural analysis
        wh_words = {"what", "how", "where", "when", "why", "who"}
        has_wh = any(w in query for w in wh_words)
        doc_score += 0.8 if has_wh else 0.0

        notes.update(
            {
                "has_wh_words": has_wh,
                "query_length": len(words),
                "has_question_mark": "?" in query,
                "punctuation_density": sum(1 for c in query if c in string.punctuation)
                / max(1, len(query)),
            }
        )

        doc_score += 0.6 if "?" in query else 0.0

        return FeatureScores(doc_score=doc_score, conv_score=conv_score, notes=notes)

    def _score_pattern_rules(self, query: str) -> FeatureScores:
        """Score the query against all pattern-based rules."""
        doc_score: float = 0.0
        conv_score: float = 0.0
        notes: Dict[str, Any] = {}
        matched_rules: List[Dict[str, Any]] = []

        for rule in self.rules:
            match_found = False

            try:
                if rule.rule_type == RuleType.KEYWORD and rule.pattern in query:
                    match_found = True
                elif rule.rule_type == RuleType.PHRASE and rule.pattern in query:
                    match_found = True
                elif rule.rule_type == RuleType.REGEX and re.search(
                    rule.pattern, query, re.IGNORECASE
                ):
                    match_found = True

                if match_found:
                    if rule.category == QueryType.DOCUMENT_RETRIEVAL:
                        doc_score += rule.weight
                    else:
                        conv_score += rule.weight

                    matched_rules.append(
                        {
                            "pattern": rule.pattern,
                            "type": rule.rule_type.value,
                            "weight": rule.weight,
                            "category": rule.category.value,
                            "description": rule.description,
                        }
                    )

            except re.error as e:
                # Log regex errors but continue processing
                notes[f"regex_error_{rule.pattern}"] = str(e)

        notes["matched_rules"] = matched_rules
        notes["total_matches"] = len(matched_rules)

        return FeatureScores(doc_score=doc_score, conv_score=conv_score, notes=notes)

    def _calculate_confidence(self, doc_score: float, conv_score: float) -> float:
        """Calculate classification confidence based on score separation and strength."""
        total = doc_score + conv_score

        if total == 0:
            return 0.5  # Neutral confidence

        separation = abs(doc_score - conv_score) / total
        strength = max(doc_score, conv_score) / self.config.max_expected_score

        confidence = (
            separation * self.config.separation_weight
            + min(strength, 1.0) * self.config.strength_weight
        )

        return min(confidence, 1.0)

    @component.output_types(
        needs_retrieval=bool,
        classification=QueryType,
        confidence=float,
        feature_scores=Dict[str, Any],
    )
    def run(self, query: str) -> Dict[str, Any]:
        """
        Analyze the query and return comprehensive classification results.

        Args:
            query: The user query to classify

        Returns:
            Dict[str, Any] with classification, confidence, and diagnostics

        Raises:
            ValueError: If query is invalid or processing fails
        """
        start_time = time.time()

        try:
            # Preprocess and validate query
            processed_query = self._preprocess_query(query)

            # Calculate scores from both approaches
            rule_scores = self._score_pattern_rules(processed_query)
            feature_scores = self._calculate_feature_scores(processed_query)

            # Combine scores
            doc_final = rule_scores.doc_score + feature_scores.doc_score
            conv_final = rule_scores.conv_score + feature_scores.conv_score

            # Determine classification and confidence
            confidence = self._calculate_confidence(doc_final, conv_final)
            classification = (
                QueryType.DOCUMENT_RETRIEVAL
                if doc_final >= conv_final
                else QueryType.CONVERSATIONAL
            )

            # Calculate processing time
            processing_time = (
                time.time() - start_time
            ) * 1000  # Convert to milliseconds

            # Compile detailed results
            detailed_scores: Dict[str, Any] = {
                "document_final_score": doc_final,
                "conversational_final_score": conv_final,
                "confidence": confidence,
                "pattern_analysis": rule_scores.notes,
                "feature_analysis": feature_scores.notes,
                "processing_metadata": {
                    "original_query": query,
                    "processed_query": processed_query,
                    "extracted_keywords": self._extract_keywords(processed_query),
                    "total_rules_evaluated": len(self.rules),
                },
            }

            # Create the Pydantic model for validation
            result = QueryClassificationResult(
                needs_retrieval=classification == QueryType.DOCUMENT_RETRIEVAL,
                classification=classification,
                confidence=confidence,
                feature_scores=detailed_scores,
                processing_time_ms=processing_time,
            )

            # Return dictionary matching the output_types
            return {
                "needs_retrieval": result.needs_retrieval,
                "classification": result.classification,
                "confidence": result.confidence,
                "feature_scores": result.feature_scores,
                "processing_time_ms": result.processing_time_ms,
            }

        except Exception as e:
            raise ValueError(f"Classification failed for query '{query}': {str(e)}")


def initialize_integrated_query_classifier(
    config: Optional[ClassificationConfig] = None,
) -> IntegratedQueryClassifier:
    """
    Factory function for creating a configured classifier instance.

    Args:
        config: Optional classification configuration

    Returns:
        Initialized IntegratedQueryClassifier
    """
    return IntegratedQueryClassifier(config=config)
