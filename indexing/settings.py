"""Indexing Settings.

This module defines the IndexingSettings class, which is used to configure settings for indexing operations.
It includes paths for source and target data, embedding model details, vectorstore configuration, record manager settings,
and indexing parameters. The settings can be loaded from environment variables specified in a .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class IndexingSettings(BaseSettings):  # type: ignore
    """
    Configuration settings for indexing operations.

    Attributes:
        src_path (str): Path to the source data directory.
        target_path (str): Path to the target data directory.
        embedding_model_name (str): Name of the embedding model to use.
        collection_name (str): Name of the vectorstore collection.
        chroma_path (str): Path to the chroma vectorstore.
        namespace (str): Namespace for the record manager.
        db_url (str): URL for the record manager database.
        chunk_size (int): Size of chunks for indexing.
        chunk_overlap (int): Overlap size between chunks.
        cleanup (str): Cleanup mode after indexing.
        model_config (SettingsConfigDict): Configuration for loading settings from environment variables.
    """

    src_path: str = "data/raw"
    target_path: str = "data/index"

    # Embedding model configuration
    embedding_model_name: str = "sentence-transformers/all-mpnet-base-v2"

    # Vectorstore configuration
    collection_name: str = "test_collection"
    chroma_path: str = f"{target_path}/chroma_vectorstore"

    # Record manager configuration
    namespace: str = f"chroma/{collection_name}"
    db_url: str = f"sqlite:///{target_path}/record_manager_cache.sql"

    # Indexing configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    cleanup: str = "full"

    # Model configuration for loading settings from environment variables
    model_config = SettingsConfigDict(env_prefix="INDEXING_", env_file=".env")
