"""Create vectorstore.

This module provides functionality to create embeddings for documents and index them using a vector store.
"""

import logging

import tiktoken
from langchain.indexes import SQLRecordManager, index
from langchain_chroma import Chroma
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_core.documents.base import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import IndexingSettings
from openai_pricing import OPENAI_EMBEDDINGS_PRICING

config = IndexingSettings()
embeddings = OpenAIEmbeddings(model=config.openai_model)
vectorstore = Chroma(
    collection_name=config.collection_name,
    embedding_function=embeddings,
    persist_directory=config.chroma_path,
)


def init_record_manager(namespace: str, db_url: str) -> SQLRecordManager:
    """Initialize and return a SQLRecordManager with the given namespace and database URL."""
    record_manager = SQLRecordManager(namespace, db_url=db_url)
    record_manager.create_schema()
    return record_manager


def load_data_chunks(knowledge_base_path: str, chunk_size: int, chunk_overlap: int) -> list[Document]:
    """Load and split documents into chunks."""
    docs = PyPDFDirectoryLoader(path=knowledge_base_path).load()
    chunks: list[Document] = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    ).split_documents(docs)
    return chunks


def calculate_embedding_cost(chunks: list[Document], openai_model: str) -> None:
    """Calculate and log the cost of embedding the document chunks."""
    model_cost = OPENAI_EMBEDDINGS_PRICING[openai_model]
    encoding = tiktoken.encoding_for_model(openai_model)
    total_tokens = 0

    for chunk in chunks:
        total_tokens += len(encoding.encode(chunk.page_content))

    total_cost = total_tokens * model_cost
    logging.info("Total tokens: %d, Total cost: %f", total_tokens, total_cost)


def index_chunks(chunks: list[Document], record_manager: SQLRecordManager, vectorstore: Chroma, cleanup: str) -> None:
    """Index the document chunks and log the result."""
    res = index(chunks, record_manager, vectorstore, cleanup=cleanup, source_id_key="source")
    logging.info("Indexing completed: %s", res)


def run_indexing_process(config: IndexingSettings) -> None:
    """Run the entire indexing process."""
    record_manager = init_record_manager(namespace=config.namespace, db_url=config.db_url)
    chunks = load_data_chunks(config.knowledge_base_path, config.chunk_size, config.chunk_overlap)
    calculate_embedding_cost(chunks, config.openai_model)
    index_chunks(chunks, record_manager, vectorstore, cleanup=config.cleanup)


if __name__ == "__main__":
    run_indexing_process(config)
