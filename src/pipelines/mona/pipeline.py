"""
Query Processing Pipeline (Main Mona Pipeline)

This module contains the initialization function for the query processing pipeline.
"""

from typing import Union

from hayhooks import log
from haystack import AsyncPipeline, Pipeline
from haystack.components.joiners import BranchJoiner

from src.components.conditional_router import initialize_mona_router
from src.components.direct_prompt_builder import initialize_direct_prompt_builder
from src.components.documents_retriever import initialize_document_retriever
from src.components.llm_generator import initialize_llm_generator
from src.components.query_classifier import initialize_integrated_query_classifier
from src.components.rag_prompt_builder import initialize_rag_prompt_builder
from src.components.text_embedder import initialize_text_embedder


def initialize_chat_pipeline(is_async: bool = False) -> Union[Pipeline, AsyncPipeline]:
    """
    Initialize a query processing pipeline with single LLM generator.

    This pipeline:
    1. Analyzes if retrieval is needed
    2. Routes to either direct prompt or RAG prompt
    3. Joins prompts and generates response using single LLM generator

    Args:
        is_async: Whether to create async or sync pipeline

    Returns:
        Configured Pipeline or AsyncPipeline
    """
    pipeline = AsyncPipeline() if is_async else Pipeline()

    try:
        log.debug("Initializing Single LLM Query Pipeline Components")

        # --- Query classification and routing ---
        pipeline.add_component(
            "query_classifier", initialize_integrated_query_classifier()
        )
        pipeline.add_component("router", initialize_mona_router())
        log.debug("Successfully initialized query_analyzer and router")

        # --- Prompt builders ---
        pipeline.add_component(
            "direct_prompt_builder", initialize_direct_prompt_builder()
        )
        pipeline.add_component("rag_prompt_builder", initialize_rag_prompt_builder())
        log.debug("Successfully initialized prompt builders")

        # --- RAG components (only needed for retrieval path) ---
        pipeline.add_component("text_embedder", initialize_text_embedder())
        pipeline.add_component("documents_retriever", initialize_document_retriever())
        log.debug("Successfully initialized RAG components")

        # --- Prompt joiner to merge outputs from both prompt builders ---
        pipeline.add_component("prompt_joiner", BranchJoiner(str))
        log.debug("Successfully initialized prompt joiner")

        # --- Single LLM generator ---
        pipeline.add_component("llm_generator", initialize_llm_generator())
        log.debug("Successfully initialized single LLM generator")

        # --- Connect components ---
        log.debug("Connecting Pipeline Components")

        # Query Classifier → Router
        pipeline.connect("query_classifier.needs_retrieval", "router.needs_retrieval")

        # Direct query path: Router → DirectPromptBuilder → PromptJoiner
        pipeline.connect("router.direct_query", "direct_prompt_builder.query")
        pipeline.connect("direct_prompt_builder.prompt", "prompt_joiner")

        # RAG path: Router → TextEmbedder → DocumentsRetriever → RAGPromptBuilder → PromptJoiner
        pipeline.connect("router.retrieval_query", "text_embedder.text")
        pipeline.connect(
            "text_embedder.embedding", "documents_retriever.query_embedding"
        )
        pipeline.connect(
            "documents_retriever.documents", "rag_prompt_builder.documents"
        )
        pipeline.connect("router.retrieval_query", "rag_prompt_builder.query")
        pipeline.connect("rag_prompt_builder.prompt", "prompt_joiner")

        # PromptJoiner → LLMGenerator
        pipeline.connect("prompt_joiner", "llm_generator.prompt")

        log.debug("Successfully connected all Pipeline Components")

        return pipeline

    except Exception as e:
        log.error(f"Failed to initialize chat pipeline: {str(e)}")
        raise
