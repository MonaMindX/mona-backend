from typing import Dict, Union

from src.components.conditional_router import initialize_mona_router


def test_initialize_mona_router_creates_router_with_two_routes() -> None:
    """
    Test that initialize_mona_router returns a ConditionalRouter with two routes.
    """

    router = initialize_mona_router()

    # Verify router is created and is a ConditionalRouter instance
    assert router is not None
    assert hasattr(router, "routes")

    # Verify two routes are configured
    assert len(router.routes) == 2

    # Verify first route (retrieval_query)
    retrieval_route = router.routes[0]
    assert retrieval_route["condition"] == "{{ needs_retrieval == True }}"
    assert retrieval_route["output"] == "{{ original_query }}"
    assert retrieval_route["output_name"] == "retrieval_query"
    assert retrieval_route["output_type"] == str

    # Verify second route (direct_query)
    direct_route = router.routes[1]
    assert direct_route["condition"] == "{{ needs_retrieval == False }}"
    assert direct_route["output"] == "{{ original_query }}"
    assert direct_route["output_name"] == "direct_query"
    assert direct_route["output_type"] == str


def test_router_routes_to_retrieval_query_when_needs_retrieval_is_true() -> None:
    """
    Test that the router routes to retrieval_query when needs_retrieval is True.
    """

    router = initialize_mona_router()

    # Test input with needs_retrieval=True
    test_input: Dict[str, Union[str, bool]] = {
        "needs_retrieval": True,
        "original_query": "What is the capital of France?",
    }

    result = router.run(  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        **test_input
    )

    # Verify the result routes to retrieval_query
    assert "retrieval_query" in result
    assert result["retrieval_query"] == "What is the capital of France?"
    assert "direct_query" not in result


def test_router_routes_to_direct_query_when_needs_retrieval_is_false() -> None:
    """
    Test that the router routes to direct_query when needs_retrieval is False.
    """

    router = initialize_mona_router()

    # Test input with needs_retrieval=False
    test_input: Dict[str, Union[str, bool]] = {
        "needs_retrieval": False,
        "original_query": "What is 2 + 2?",
    }

    result = router.run(  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        **test_input
    )

    # Verify the result routes to direct_query
    assert "direct_query" in result
    assert result["direct_query"] == "What is 2 + 2?"
    assert "retrieval_query" not in result


def test_initialize_mona_router_returns_conditional_router_instance_with_correct_conditions() -> (
    None
):
    """
    Test that initialize_mona_router returns a ConditionalRouter instance with correct route conditions.
    """

    router = initialize_mona_router()

    # Verify router is a ConditionalRouter instance
    assert router is not None
    assert hasattr(router, "routes")

    # Verify correct route conditions are set
    routes = router.routes
    assert len(routes) == 2

    # Check first route condition
    assert routes[0]["condition"] == "{{ needs_retrieval == True }}"

    # Check second route condition
    assert routes[1]["condition"] == "{{ needs_retrieval == False }}"
