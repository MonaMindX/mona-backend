"""
The Conditional Router that routes queries based on intent analysis results.
"""

from typing import List

from haystack.components.routers.conditional_router import ConditionalRouter, Route


def initialize_mona_router() -> ConditionalRouter:
    """
    Initialize the conditional router for Mona chat pipeline.

    Routes queries based on intent analysis results to either:
    - retrieval_query: Query needs document retrieval
    - direct_query: Query can be answered directly

    Returns:
        Configured ConditionalRouter instance
    """
    routes: List[Route] = [
        {
            "condition": "{{ needs_retrieval == True }}",
            "output": "{{ original_query }}",
            "output_name": "retrieval_query",
            "output_type": str,
        },
        {
            "condition": "{{ needs_retrieval == False }}",
            "output": "{{ original_query }}",
            "output_name": "direct_query",
            "output_type": str,
        },
    ]
    return ConditionalRouter(routes=routes)
