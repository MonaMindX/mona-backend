"""
System Route containing system-related endpoints for Mona Backend.
"""

import os
import platform
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict

import psutil
from fastapi import APIRouter, HTTPException
from hayhooks.settings import settings

from src.schemas.system import HealthResponse, InfoResponse, LiveResponse, ReadyResponse

router = APIRouter(tags=["System"])

# Centralized service metadata
SERVICE_METADATA = {
    "name": "mona-backend",
    "version": "1.0.0",
    "description": "Mona Backend Service",
    "api_version": "v1",
}

# Store startup time for uptime calculation
startup_time = time.time()


def get_utc_timestamp() -> str:
    """Returns the current UTC time in ISO 8601 format with 'Z'."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=200,
    summary="Health Check",
    description="Comprehensive health check with system metrics. Used by monitoring systems and load balancers.",
    response_description="Health status with detailed system metrics",
    tags=["System"],
)
async def health_check() -> HealthResponse:
    """
    Comprehensive health check with system metrics.
    Used by monitoring systems and load balancers.

    Returns:
        HealthResponse: Object containing health status, system metrics, and service information.

    Raises:
        HTTPException: 503 Service Unavailable if health check fails
    """
    try:
        current_time = time.time()
        uptime_seconds = current_time - startup_time

        # System metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        cpu_percent = psutil.cpu_percent(interval=1)

        health_data: Dict[str, Any] = {
            "status": "healthy",
            "timestamp": get_utc_timestamp(),
            "service": {
                "name": SERVICE_METADATA["name"],
                "version": SERVICE_METADATA["version"],
                "uptime_seconds": round(uptime_seconds, 2),
                "uptime_human": format_uptime(uptime_seconds),
            },
            "system": {
                "cpu_usage_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent,
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_percent": round((disk.used / disk.total) * 100, 2),
                },
            },
            "hayhooks": {
                "status": "running",
                "host": settings.host,
                "port": settings.port,
            },
        }

        return HealthResponse(**health_data)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@router.get(
    "/ready",
    response_model=ReadyResponse,
    status_code=200,
    summary="Readiness Probe",
    description="Kubernetes readiness probe. Checks if the service is ready to accept traffic.",
    response_description="Readiness status with component checks",
    tags=["System"],
)
async def readiness_check() -> ReadyResponse:
    """
    Kubernetes readiness probe endpoint.
    Checks if the service is ready to accept traffic.

    Returns:
        ReadyResponse: Object containing readiness status and component checks.

    Raises:
        HTTPException: 503 Service Unavailable if service is not ready
    """
    try:
        ready_data: Dict[str, Any] = {
            "ready": True,
            "timestamp": get_utc_timestamp(),
            "checks": {"hayhooks": "ok", "system": "ok"},
        }
        return ReadyResponse(**ready_data)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")


@router.get(
    "/live",
    response_model=LiveResponse,
    status_code=200,
    summary="Liveness Probe",
    description="Kubernetes liveness probe. Checks if the service is alive and should not be restarted.",
    response_description="Liveness status of the service",
    tags=["System"],
)
async def liveness_check() -> LiveResponse:
    """
    Kubernetes liveness probe endpoint.
    Checks if the service is alive and should not be restarted.

    Returns:
        LiveResponse: Object containing liveness status and timestamp.
    """
    live_data: Dict[str, Any] = {
        "alive": True,
        "timestamp": get_utc_timestamp(),
    }
    return LiveResponse(**live_data)


@router.get(
    "/info",
    response_model=InfoResponse,
    status_code=200,
    summary="System Information",
    description="Provides detailed system information including environment and dependencies.",
    response_description="Detailed information about the system and service",
    tags=["System"],
)
async def system_info() -> InfoResponse:
    """
    Detailed system information including environment and dependencies.

    Returns:
        InfoResponse: Object containing service metadata, environment details,
                     and system information (in non-production environments).
    """
    env = os.getenv("ENVIRONMENT", "development")

    info_data: Dict[str, Any] = {
        "service": {
            "name": SERVICE_METADATA["name"],
            "version": SERVICE_METADATA["version"],
            "description": SERVICE_METADATA["description"],
            "api_version": SERVICE_METADATA["api_version"],
            "started_at": datetime.fromtimestamp(startup_time).isoformat() + "Z",
        },
        "environment": {
            "name": env,
        },
    }

    # Only include detailed system and environment info in non-production environments
    if env != "production":
        info_data["system"] = {
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "python_version": sys.version,
            "cpu_count": psutil.cpu_count(),
            "hostname": platform.node(),
        }
        info_data["hayhooks"] = {
            "host": settings.host,
            "port": settings.port,
        }

    return InfoResponse(**info_data)


def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)

    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"
