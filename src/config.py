"""Config.

This module provides configuration settings for the chatbot and indexing functionalities.
"""

import logging

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class ChatbotSettings(BaseSettings):  # type: ignore[misc]
    """Settings for the chatbot."""

    openai_model: str = "gpt-4o-mini"
    prompt_name: str = "rlm/rag-prompt"
    max_num_context_sources: int = 10
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class IndexingSettings(BaseSettings):  # type: ignore[misc]
    """Settings for indexing."""

    knowledge_base_path: str = "data/raw"
    openai_model: str = "text-embedding-3-large"
    collection_name: str = "3Dfindit"
    chunk_size: int = Field(default=1000, gt=0)
    chunk_overlap: int = Field(default=200, ge=0)
    cleanup: str = "full"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", nested_model_default_partial_update=True)

    @computed_field
    def vectorstore_path(self) -> str:
        """Path to the vector store based on the OpenAI model."""
        return f"vectorstore/{self.openai_model}"

    @computed_field
    def chroma_path(self) -> str:
        """Path to the chroma database."""
        return f"{self.vectorstore_path}/chroma_db"

    @computed_field
    def namespace(self) -> str:
        """Namespace for the chroma collection."""
        return f"chroma/{self.collection_name}"

    @computed_field
    def db_url(self) -> str:
        """URL for the SQLite database."""
        return f"sqlite:///{self.vectorstore_path}/record_manager_cache.sql"

    @field_validator("chunk_size", "chunk_overlap")
    def check_positive(cls: "IndexingSettings", v: int) -> int:  # noqa: N805
        """Validate that chunk_size and chunk_overlap are positive integers."""
        if v < 0:
            msg = "must be a positive integer"
            raise ValueError(msg)
        return v
