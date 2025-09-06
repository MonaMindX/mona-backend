"""
Pydantic models for system route responses.
"""

from typing import Dict, Optional

from pydantic import BaseModel, Field


# Models for /health endpoint
class HealthService(BaseModel):
    name: str = Field(
        ..., description="Name of the service.", examples=["mona-backend"]
    )
    version: str = Field(..., description="Version of the service.", examples=["1.0.0"])
    uptime_seconds: float = Field(
        ..., description="Service uptime in seconds.", examples=[3661.0]
    )
    uptime_human: str = Field(
        ..., description="Human-readable service uptime.", examples=["1h 1m 1s"]
    )


class HealthSystemMemory(BaseModel):
    total_gb: float = Field(
        ..., description="Total system memory in GB.", examples=[8.0]
    )
    available_gb: float = Field(
        ..., description="Available system memory in GB.", examples=[4.0]
    )
    used_percent: float = Field(
        ..., description="Memory usage percentage.", examples=[50.0]
    )


class HealthSystemDisk(BaseModel):
    total_gb: float = Field(
        ..., description="Total disk space in GB.", examples=[100.0]
    )
    free_gb: float = Field(..., description="Free disk space in GB.", examples=[50.0])
    used_percent: float = Field(
        ..., description="Disk usage percentage.", examples=[50.0]
    )


class HealthSystem(BaseModel):
    cpu_usage_percent: float = Field(
        ..., description="Current CPU usage percentage.", examples=[25.5]
    )
    memory: HealthSystemMemory = Field(..., description="System memory metrics.")
    disk: HealthSystemDisk = Field(..., description="System disk metrics.")


class HealthHayhooks(BaseModel):
    status: str = Field(
        ..., description="Status of the Hayhooks component.", examples=["running"]
    )
    host: str = Field(
        ..., description="Host where Hayhooks is running.", examples=["localhost"]
    )
    port: int = Field(
        ..., description="Port on which Hayhooks is running.", examples=[1414]
    )


class HealthResponse(BaseModel):
    status: str = Field(
        ..., description="Overall health status of the service.", examples=["healthy"]
    )
    timestamp: str = Field(
        ...,
        description="UTC timestamp of the health check.",
        examples=["2024-01-15T10:30:00.000000Z"],
    )
    service: HealthService = Field(
        ..., description="Service-specific health information."
    )
    system: HealthSystem = Field(..., description="System-level health metrics.")
    hayhooks: HealthHayhooks = Field(
        ..., description="Health information for the Hayhooks component."
    )


# Models for /ready endpoint
class ReadyResponse(BaseModel):
    ready: bool = Field(
        ...,
        description="Indicates if the service is ready to accept traffic.",
        examples=[True],
    )
    timestamp: str = Field(
        ...,
        description="UTC timestamp of the readiness check.",
        examples=["2024-01-15T10:30:00.000000Z"],
    )
    checks: Dict[str, str] = Field(
        ...,
        description="Status of individual readiness checks.",
        examples=[{"hayhooks": "ok", "system": "ok"}],
    )


# Models for /live endpoint
class LiveResponse(BaseModel):
    alive: bool = Field(
        ..., description="Indicates if the service is alive.", examples=[True]
    )
    timestamp: str = Field(
        ...,
        description="UTC timestamp of the liveness check.",
        examples=["2024-01-15T10:30:00.000000Z"],
    )


# Models for /info endpoint
class InfoService(BaseModel):
    name: str = Field(
        ..., description="Name of the service.", examples=["mona-backend"]
    )
    version: str = Field(..., description="Version of the service.", examples=["1.0.0"])
    description: str = Field(
        ...,
        description="Description of the service.",
        examples=["Mona Backend Service"],
    )
    api_version: str = Field(..., description="Current API version.", examples=["v1"])
    started_at: str = Field(
        ...,
        description="UTC timestamp when the service started.",
        examples=["2024-01-15T10:00:00.000000Z"],
    )


class InfoEnvironment(BaseModel):
    name: str = Field(
        ..., description="Deployment environment.", examples=["development"]
    )


class InfoSystem(BaseModel):
    platform: str = Field(
        ...,
        description="Operating system platform.",
        examples=["Linux-5.10.0-x86_64-with-glibc2.31"],
    )
    architecture: str = Field(
        ..., description="System architecture.", examples=["64bit"]
    )
    processor: str = Field(
        ..., description="Processor information.", examples=["x86_64"]
    )
    python_version: str = Field(
        ...,
        description="Version of the Python interpreter.",
        examples=["3.11.5 (main, Aug 24 2023, 15:09:45) [GCC 11.3.0] on linux"],
    )
    cpu_count: int = Field(..., description="Number of CPU cores.", examples=[8])
    hostname: str = Field(
        ..., description="Hostname of the machine.", examples=["mona-prod-server"]
    )


class InfoHayhooks(BaseModel):
    host: str = Field(
        ...,
        description="Host where Hayhooks is configured to run.",
        examples=["localhost"],
    )
    port: int = Field(
        ..., description="Port on which Hayhooks is configured to run.", examples=[1414]
    )


class InfoResponse(BaseModel):
    service: InfoService = Field(..., description="Service metadata.")
    environment: InfoEnvironment = Field(
        ..., description="Service runtime environment details."
    )
    system: Optional[InfoSystem] = Field(
        None, description="Underlying system information (only in non-production)."
    )
    hayhooks: Optional[InfoHayhooks] = Field(
        None, description="Hayhooks configuration details (only in non-production)."
    )
