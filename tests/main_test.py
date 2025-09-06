"""
Main App Tests
"""

import runpy
import sys
from unittest.mock import patch

from fastapi.testclient import TestClient


def test_root_endpoint() -> None:
    """
    Test that the FastAPI app is created successfully.
    """
    from src.main import create_application

    app = create_application()
    client = TestClient(app)
    response = client.get("/")
    # No root so expect a 404
    assert response.status_code == 404


def test_main_entrypoint_runs_uvicorn() -> None:
    """Test that the main entrypoint calls uvicorn.run."""
    with patch("src.main.uvicorn.run") as mock_run:
        # Remove src.main from cache to allow runpy to execute it fresh
        if "src.main" in sys.modules:
            del sys.modules["src.main"]

        runpy.run_module("src.main", run_name="__main__")
        mock_run.assert_called_once()
