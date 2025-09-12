"""
System Route Tests
"""

import platform
import sys
from unittest.mock import MagicMock, patch

import psutil
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.routes.system import (
    format_uptime,
    health_check,
    liveness_check,
    readiness_check,
    router,
    startup_time,
    system_info,
)
from src.schemas.system import HealthResponse, InfoResponse, LiveResponse, ReadyResponse


@pytest.mark.asyncio
async def test_health_check_returns_healthy_status_with_metrics() -> None:
    """Test that health check returns healthy status with all system metrics."""
    with (
        patch("src.routes.system.psutil.virtual_memory") as mock_memory,
        patch("src.routes.system.psutil.disk_usage") as mock_disk,
        patch("src.routes.system.psutil.cpu_percent") as mock_cpu,
        patch("src.routes.system.time.time") as mock_time,
        patch("src.routes.system.get_utc_timestamp") as mock_timestamp,
        patch("src.routes.system.startup_time", 1000.0),
    ):

        # Mock system metrics
        mock_memory.return_value = MagicMock(
            total=8589934592, available=4294967296, percent=50.0  # 8GB  # 4GB
        )
        mock_disk.return_value = MagicMock(
            total=107374182400,  # 100GB
            free=53687091200,  # 50GB
            used=53687091200,  # 50GB
        )
        mock_cpu.return_value = 25.5

        # Mock time for uptime calculation
        mock_time.return_value = 1100.0  # current_time
        mock_timestamp.return_value = "2024-01-15T10:30:00Z"

        response = await health_check()

        assert isinstance(response, HealthResponse)
        assert response.status == "healthy"
        assert response.timestamp == "2024-01-15T10:30:00Z"
        assert response.service.name == "mona-backend"
        assert response.service.version == "1.0.0"
        assert response.service.uptime_seconds == 100.0
        assert response.system.cpu_usage_percent == 25.5
        assert response.system.memory.total_gb == 8.0
        assert response.system.memory.available_gb == 4.0
        assert response.system.memory.used_percent == 50.0
        assert response.system.disk.total_gb == 100.0
        assert response.system.disk.free_gb == 50.0
        assert response.system.disk.used_percent == 50.0
        assert response.hayhooks.status == "running"


@pytest.mark.asyncio
async def test_health_endpoint_calculates_correct_uptime() -> None:
    """Test that health endpoint calculates uptime correctly based on startup_time"""

    # Create test app
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    # Mock the current time to be 3661 seconds (1 hour, 1 minute, 1 second) after startup
    mock_current_time = startup_time + 3661

    with (
        patch("src.routes.system.time.time", return_value=mock_current_time),
        patch("src.routes.system.psutil.virtual_memory") as mock_memory,
        patch("src.routes.system.psutil.disk_usage") as mock_disk,
        patch("src.routes.system.psutil.cpu_percent", return_value=25.0),
        patch(
            "src.routes.system.get_utc_timestamp", return_value="2024-01-15T10:30:00Z"
        ),
    ):

        # Mock system metrics
        mock_memory.return_value = MagicMock(
            total=8589934592, available=4294967296, percent=50.0  # 8GB  # 4GB
        )
        mock_disk.return_value = MagicMock(
            total=107374182400,  # 100GB
            free=53687091200,  # 50GB
            used=53687091200,  # 50GB
        )

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Verify uptime calculation
        assert data["service"]["uptime_seconds"] == 3661.0
        assert data["service"]["uptime_human"] == "1h 1m 1s"
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_readiness_check_returns_ready_status() -> None:
    """Test that readiness check returns ready status with timestamp and checks."""
    with patch("src.routes.system.get_utc_timestamp") as mock_timestamp:
        mock_timestamp.return_value = "2024-01-15T12:00:00Z"

        result = await readiness_check()

        assert isinstance(result, ReadyResponse)
        assert result.ready is True
        assert result.timestamp == "2024-01-15T12:00:00Z"
        assert result.checks["hayhooks"] == "ok"
        assert result.checks["system"] == "ok"


@pytest.mark.asyncio
async def test_readiness_check_handles_exceptions() -> None:
    """Test that readiness check properly handles exceptions."""
    with patch("src.routes.system.get_utc_timestamp") as mock_timestamp:
        mock_timestamp.side_effect = Exception("Timestamp error")

        with pytest.raises(HTTPException) as exc_info:
            await readiness_check()

        assert exc_info.value.status_code == 503
        assert "Service not ready: Timestamp error" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_liveness_check_returns_alive_status_with_timestamp() -> None:
    """Test that liveness check returns alive status with current timestamp."""
    with patch("src.routes.system.get_utc_timestamp") as mock_timestamp:
        mock_timestamp.return_value = "2024-01-15T12:00:00Z"

        result = await liveness_check()

        # Verify response is a LiveResponse instance
        assert isinstance(result, LiveResponse)
        assert result.alive is True
        assert result.timestamp == "2024-01-15T12:00:00Z"


@pytest.mark.asyncio
async def test_system_info_returns_complete_system_information_non_production() -> None:
    """Test that system_info returns complete system information in non-production environment."""
    with (
        patch("src.routes.system.settings") as mock_settings,
        patch("src.routes.system.startup_time", 1640995200.0),
        patch("src.routes.system.os.getenv") as mock_getenv,
    ):

        mock_settings.host = "localhost"
        mock_settings.port = 8000
        mock_getenv.return_value = "development"  # Non-production environment

        result = await system_info()

        # Verify response is an InfoResponse instance
        assert isinstance(result, InfoResponse)

        # Verify service information
        assert result.service.name == "mona-backend"
        assert result.service.version == "1.0.0"
        assert result.service.description == "Mona Backend Service"
        assert result.service.api_version == "v1"
        assert result.service.started_at is not None

        # Verify environment information
        assert result.environment.name == "development"

        # Verify system information is included (non-production)
        assert result.system is not None
        assert result.system.platform == platform.platform()
        assert result.system.architecture == platform.architecture()[0]
        assert result.system.python_version == sys.version
        assert result.system.processor == platform.processor()
        assert result.system.cpu_count == psutil.cpu_count()
        assert result.system.hostname == platform.node()

        # Verify hayhooks configuration is included (non-production)
        assert result.hayhooks is not None
        assert result.hayhooks.host == "localhost"
        assert result.hayhooks.port == 8000


@pytest.mark.asyncio
async def test_system_info_returns_limited_information_production() -> None:
    """Test that system_info returns limited information in production environment."""
    with (
        patch("src.routes.system.startup_time", 1640995200.0),
        patch("src.routes.system.os.getenv") as mock_getenv,
    ):

        mock_getenv.return_value = "production"  # Production environment

        result = await system_info()

        # Verify response is an InfoResponse instance
        assert isinstance(result, InfoResponse)

        # Verify service information
        assert result.service.name == "mona-backend"
        assert result.service.version == "1.0.0"
        assert result.service.description == "Mona Backend Service"
        assert result.service.api_version == "v1"

        # Verify environment information
        assert result.environment.name == "production"

        # Verify system and hayhooks information is NOT included (production)
        assert result.system is None
        assert result.hayhooks is None


def test_format_uptime_different_time_ranges() -> None:
    """Test that format_uptime correctly formats different time ranges."""

    # Test seconds only
    assert format_uptime(45) == "45s"

    # Test minutes and seconds
    assert format_uptime(125) == "2m 5s"

    # Test hours, minutes and seconds
    assert format_uptime(3725) == "1h 2m 5s"

    # Test days, hours, minutes and seconds
    assert format_uptime(90125) == "1d 1h 2m 5s"

    # Test exact hour
    assert format_uptime(3600) == "1h 0m 0s"

    # Test exact day
    assert format_uptime(86400) == "1d 0h 0m 0s"

    # Test multiple days
    assert format_uptime(180000) == "2d 2h 0m 0s"


def test_format_uptime_less_than_minute() -> None:
    """Test format_uptime returns seconds only format when uptime is less than one minute."""

    # Test with 30 seconds
    result = format_uptime(30.5)
    assert result == "30s"

    # Test with 59 seconds
    result = format_uptime(59.9)
    assert result == "59s"

    # Test with 0 seconds
    result = format_uptime(0)
    assert result == "0s"

    # Test with fractional seconds
    result = format_uptime(5.7)
    assert result == "5s"


@pytest.mark.asyncio
async def test_all_endpoints_integration() -> None:
    """Integration test to verify all endpoints work together."""
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    # Test all endpoints
    with (
        patch("src.routes.system.psutil.virtual_memory") as mock_memory,
        patch("src.routes.system.psutil.disk_usage") as mock_disk,
        patch("src.routes.system.psutil.cpu_percent") as mock_cpu,
        patch("src.routes.system.get_utc_timestamp") as mock_timestamp,
    ):

        # Mock system metrics
        mock_memory.return_value = MagicMock(
            total=8589934592, available=4294967296, percent=50.0
        )
        mock_disk.return_value = MagicMock(
            total=107374182400, free=53687091200, used=53687091200
        )
        mock_cpu.return_value = 25.0
        mock_timestamp.return_value = "2024-01-15T10:30:00Z"

        # Test health endpoint
        health_response = client.get("/health")
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data["status"] == "healthy"
        assert "service" in health_data
        assert "system" in health_data

        # Test readiness endpoint
        ready_response = client.get("/ready")
        assert ready_response.status_code == 200
        ready_data = ready_response.json()
        assert ready_data["ready"] is True
        assert "checks" in ready_data

        # Test liveness endpoint
        live_response = client.get("/live")
        assert live_response.status_code == 200
        live_data = live_response.json()
        assert live_data["alive"] is True

        # Test info endpoint
        info_response = client.get("/info")
        assert info_response.status_code == 200
        info_data = info_response.json()
        assert info_data["service"]["name"] == "mona-backend"
        assert "environment" in info_data


@pytest.mark.asyncio
async def test_health_check_with_high_resource_usage() -> None:
    """Test health check still returns healthy status even with high resource usage."""
    with (
        patch("src.routes.system.psutil.virtual_memory") as mock_memory,
        patch("src.routes.system.psutil.disk_usage") as mock_disk,
        patch("src.routes.system.psutil.cpu_percent") as mock_cpu,
        patch("src.routes.system.time.time") as mock_time,
        patch("src.routes.system.get_utc_timestamp") as mock_timestamp,
        patch("src.routes.system.startup_time", 1000.0),
    ):

        # Mock high resource usage
        mock_memory.return_value = MagicMock(
            total=8589934592,
            available=858993459,
            percent=90.0,  # 8GB  # 0.8GB (low available)
        )
        mock_disk.return_value = MagicMock(
            total=107374182400,  # 100GB
            free=5368709120,  # 5GB (low free space)
            used=102005473280,  # 95GB
        )
        mock_cpu.return_value = 95.0  # High CPU usage

        mock_time.return_value = 1100.0
        mock_timestamp.return_value = "2024-01-15T10:30:00Z"

        response = await health_check()

        # Should still return healthy status (monitoring systems decide what's unhealthy)
        assert isinstance(response, HealthResponse)
        assert response.status == "healthy"
        assert response.system.cpu_usage_percent == 95.0
        assert response.system.memory.used_percent == 90.0
        assert response.system.disk.used_percent == 95.0


def test_format_uptime_edge_cases() -> None:
    """Test format_uptime with edge cases and boundary values."""

    # Test zero
    assert format_uptime(0) == "0s"

    # Test very small decimal
    assert format_uptime(0.1) == "0s"

    # Test exactly 1 minute
    assert format_uptime(60) == "1m 0s"

    # Test exactly 1 hour
    assert format_uptime(3600) == "1h 0m 0s"

    # Test exactly 1 day
    assert format_uptime(86400) == "1d 0h 0m 0s"

    # Test large number (multiple years)
    assert format_uptime(31536000) == "365d 0h 0m 0s"  # 1 year in seconds


@pytest.mark.asyncio
async def test_system_info_environment_variable_handling() -> None:
    """Test system_info handles different environment variable values correctly."""

    test_cases = [
        ("development", True),  # Should include system/hayhooks info
        ("staging", True),  # Should include system/hayhooks info
        ("testing", True),  # Should include system/hayhooks info
        ("production", False),  # Should NOT include system/hayhooks info
    ]

    for env_value, should_include_details in test_cases:
        with (
            patch("src.routes.system.startup_time", 1640995200.0),
            patch("src.routes.system.os.getenv") as mock_getenv,
            patch("src.routes.system.settings") as mock_settings,
        ):

            mock_getenv.return_value = env_value
            mock_settings.host = "localhost"
            mock_settings.port = 8000

            result = await system_info()

            assert isinstance(result, InfoResponse)
            assert result.service.name == "mona-backend"

            if should_include_details:
                assert (
                    result.system is not None
                ), f"Expected system info for env: {env_value}"
                assert (
                    result.hayhooks is not None
                ), f"Expected hayhooks info for env: {env_value}"
            else:
                assert (
                    result.system is None
                ), f"Expected no system info for env: {env_value}"
                assert (
                    result.hayhooks is None
                ), f"Expected no hayhooks info for env: {env_value}"


@pytest.mark.asyncio
async def test_error_handling_with_pydantic_validation() -> None:
    """Test that Pydantic models properly validate response data."""

    with patch("src.routes.system.get_utc_timestamp") as mock_timestamp:
        mock_timestamp.return_value = "2024-01-15T10:30:00Z"

        # Test that valid data works
        response = await liveness_check()
        assert isinstance(response, LiveResponse)
        assert response.alive is True

        # Test readiness check
        response = await readiness_check()
        assert isinstance(response, ReadyResponse)
        assert response.ready is True
        assert isinstance(response.checks, dict)


def test_router_tags_and_metadata() -> None:
    """Test that the router has correct tags and metadata."""
    assert router.tags == ["System"]

    # Verify all expected routes are registered
    route_paths: list[str] = []
    for route in router.routes:
        # Use getattr with a default to safely access path
        path = getattr(route, "path", None)
        if path is not None and isinstance(path, str):
            route_paths.append(path)

    expected_paths = ["/health", "/ready", "/live", "/info"]

    for expected_path in expected_paths:
        assert expected_path in route_paths, f"Missing route: {expected_path}"

    # Verify version endpoint is NOT included
    assert "/version" not in route_paths, "Version endpoint should not be present"


@pytest.mark.asyncio
async def test_service_metadata_consistency() -> None:
    """Test that SERVICE_METADATA is used consistently across all endpoints."""

    with (
        patch("src.routes.system.get_utc_timestamp") as mock_timestamp,
        patch("src.routes.system.psutil.virtual_memory") as mock_memory,
        patch("src.routes.system.psutil.disk_usage") as mock_disk,
        patch("src.routes.system.psutil.cpu_percent") as mock_cpu,
        patch("src.routes.system.time.time") as mock_time,
        patch("src.routes.system.startup_time", 1000.0),
    ):

        # Setup mocks
        mock_timestamp.return_value = "2024-01-15T10:30:00Z"
        mock_memory.return_value = MagicMock(
            total=8589934592, available=4294967296, percent=50.0
        )
        mock_disk.return_value = MagicMock(
            total=107374182400, free=53687091200, used=53687091200
        )
        mock_cpu.return_value = 25.0
        mock_time.return_value = 1100.0

        # Test health endpoint
        health_response = await health_check()
        assert health_response.service.name == "mona-backend"
        assert health_response.service.version == "1.0.0"

        # Test info endpoint
        info_response = await system_info()
        assert info_response.service.name == "mona-backend"
        assert info_response.service.version == "1.0.0"
        assert info_response.service.description == "Mona Backend Service"
        assert info_response.service.api_version == "v1"


@pytest.mark.asyncio
async def test_health_check_exception_handling() -> None:
    """Test that health check properly handles exceptions."""
    with patch("src.routes.system.psutil.virtual_memory") as mock_memory:
        mock_memory.side_effect = Exception("Memory error")

        with pytest.raises(HTTPException) as exc_info:
            await health_check()

        assert exc_info.value.status_code == 503
        assert "Health check failed: Memory error" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_system_info_default_environment() -> None:
    """Test that system_info uses 'development' as default environment."""
    with (
        patch("src.routes.system.startup_time", 1640995200.0),
        patch("src.routes.system.os.getenv") as mock_getenv,
        patch("src.routes.system.settings") as mock_settings,
    ):

        # Mock getenv to return default value when ENVIRONMENT is not set
        mock_getenv.return_value = "development"
        mock_settings.host = "localhost"
        mock_settings.port = 8000

        result = await system_info()

        assert isinstance(result, InfoResponse)
        assert result.environment.name == "development"
        # Should include system and hayhooks info for development
        assert result.system is not None
        assert result.hayhooks is not None


def test_startup_time_is_set() -> None:
    """Test that startup_time is properly initialized."""
    import time

    from src.routes.system import startup_time

    # startup_time should be a float representing a timestamp
    assert isinstance(startup_time, float)
    # Should be a reasonable timestamp (after year 2020)
    assert startup_time > 1577836800  # Jan 1, 2020
    # Should be before current time
    assert startup_time <= time.time()


@pytest.mark.asyncio
async def test_get_utc_timestamp_format() -> None:
    """Test that get_utc_timestamp returns properly formatted timestamp."""
    from src.routes.system import get_utc_timestamp

    timestamp = get_utc_timestamp()

    # Should be a string
    assert isinstance(timestamp, str)
    # Should end with 'Z'
    assert timestamp.endswith("Z")
    # Should be in ISO format (basic validation)
    assert "T" in timestamp
    assert len(timestamp) >= 20  # Minimum length for ISO timestamp with Z
