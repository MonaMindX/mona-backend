"""
Application Configuration Settings

These settings are used to configure the application and its behavior.
"""

from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings

from src.components.document_store import initialize_document_store


class Settings(BaseSettings):
    """
    Application configuration settings, loaded from environment variables.

    These settings are validated using Pydantic to ensure type safety and correctness.
    """

    # Hayhooks Configuration
    hayhooks_pipelines_dir: Optional[str] = Field(
        default=None,
        description="Directory containing Hayhooks pipelines. Can be an absolute or relative path.",
    )
    hayhooks_host: str = Field(
        default="localhost",
        min_length=1,
        description="The hostname or IP address for the Hayhooks server.",
    )
    hayhooks_port: int = Field(
        default=1416,
        gt=0,
        le=65535,
        description="The network port for the Hayhooks server (1-65535).",
    )

    # Database Configuration
    pg_conn_str: str = Field(default="Connection string", description="Database URL")

    # Application Behavior
    log: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="The logging level for the application."
    )
    environment: Literal["development", "production", "test"] = Field(
        default="development",
        description="The runtime environment, controlling features like debug info.",
    )

    # Document Splitter Configuration
    document_splitter_split_by: Literal[
        "function", "page", "passage", "period", "word", "line", "sentence"
    ] = Field(default="sentence", description="The method used to split documents.")
    document_splitter_language: Literal["en", "de"] = Field(
        default="en", description="The language of the documents."
    )
    document_splitter_split_length: int = Field(
        default=1000, gt=0, description="The maximum length of each split document."
    )
    document_splitter_split_overlap: int = Field(
        default=0, ge=0, description="The overlap between split documents."
    )

    # OpenAI Configuration
    openai_api_base_url: str = Field(
        default="http://192.168.43.39:1234/v1",
        description="OpenAI URL base for the local api.",
    )
    openai_api_key: str = Field(
        default="Nothing",
        description="OpenAI API key for accessing the local api.",
    )

    # Document & Text Embedders Configuration
    embedder_embedding_model: str = Field(
        default="text-embedding-qwen3-embedding-0.6b",
        description="The embedding model to use for document embedding.",
    )
    embedder_dimensions: int = Field(
        default=1024, gt=0, description="The dimensionality of the document embeddings."
    )
    embedder_timeout: float = Field(
        default=600.0, gt=0, description="The timeout for document embedding."
    )

    # Document Store & Retriever Configuration
    document_store_embedding_dimensions: int = Field(
        default=1024,
        gt=0,
        description="The dimensionality of the document store embeddings.",
    )
    document_store_vector_function: Literal[
        "cosine_similarity", "inner_product", "l2_distance"
    ] = Field(
        default="cosine_similarity",
        description="The similarity function to use for vector similarity.",
    )
    document_store_recreate_table: bool = Field(
        default=False,
        description="Whether to recreate the document store table if it already exists.",
    )
    document_store_search_strategy: Literal["exact_nearest_neighbor", "hnsw"] = Field(
        default="exact_nearest_neighbor",
        description="The search strategy to use for vector similarity.",
    )

    class ConfigDict:
        """Pydantic model configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance, accessible throughout the application
settings = Settings()

# Global document store to be accessed throughout the application
document_store = initialize_document_store(
    embedding_dimension=settings.embedder_dimensions,
    vector_function=settings.document_store_vector_function,
    recreate_table=settings.document_store_recreate_table,
    search_strategy=settings.document_store_search_strategy,
)
