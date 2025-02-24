from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents.base import Document

from config import IndexingSettings
from create_vectorstore import (
    calculate_embedding_cost,
    index_chunks,
    init_record_manager,
    load_data_chunks,
    run_indexing_process,
)


@pytest.fixture
def config():
    return IndexingSettings(
        knowledge_base_path="test_data/raw",
        openai_model="test-model",
        collection_name="test-collection",
        chunk_size=1000,
        chunk_overlap=200,
        cleanup="full",
    )


def test_init_record_manager(config):
    with patch("create_embeddings.SQLRecordManager") as MockSQLRecordManager:
        mock_instance = MockSQLRecordManager.return_value
        record_manager = init_record_manager(config.namespace, config.db_url)
        MockSQLRecordManager.assert_called_once_with(config.namespace, db_url=config.db_url)
        mock_instance.create_schema.assert_called_once()
        assert record_manager == mock_instance


def test_load_data_chunks(config):
    with patch("create_embeddings.PyPDFDirectoryLoader") as MockLoader:
        mock_loader_instance = MockLoader.return_value
        mock_loader_instance.load.return_value = [MagicMock(spec=Document)]

        with patch("create_embeddings.RecursiveCharacterTextSplitter") as MockSplitter:
            mock_splitter_instance = MockSplitter.return_value
            mock_splitter_instance.split_documents.return_value = [MagicMock(spec=Document)]

            chunks = load_data_chunks(config.knowledge_base_path, config.chunk_size, config.chunk_overlap)
            MockLoader.assert_called_once_with(path=config.knowledge_base_path)
            mock_loader_instance.load.assert_called_once()
            MockSplitter.assert_called_once_with(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
            mock_splitter_instance.split_documents.assert_called_once()
            assert chunks == mock_splitter_instance.split_documents.return_value


def test_calculate_embedding_cost(config):
    chunks = [MagicMock(spec=Document) for _ in range(5)]
    for chunk in chunks:
        chunk.page_content = "test content"

    with patch("create_embeddings.tiktoken.encoding_for_model") as MockEncoding:
        mock_encoding_instance = MockEncoding.return_value
        mock_encoding_instance.encode.return_value = [1, 2, 3]

        with patch("create_embeddings.OPENAI_EMBEDDING_PRICING", {"test-model": 0.0001}):
            with patch("create_embeddings.logging.info") as mock_logging_info:
                calculate_embedding_cost(chunks, config.openai_model)
                MockEncoding.assert_called_once_with(config.openai_model)
                assert mock_encoding_instance.encode.call_count == len(chunks)
                assert mock_logging_info.call_count == 1


def test_index_chunks(config):
    chunks = [MagicMock(spec=Document) for _ in range(5)]
    record_manager = MagicMock()
    vectorstore = MagicMock()

    with patch("create_embeddings.index") as mock_index:
        with patch("create_embeddings.logging.info") as mock_logging_info:
            index_chunks(chunks, record_manager, vectorstore, cleanup=config.cleanup)
            mock_index.assert_called_once_with(
                chunks, record_manager, vectorstore, cleanup=config.cleanup, source_id_key="source"
            )
            assert mock_logging_info.call_count == 1


def test_run_indexing_process(config):
    with patch("create_embeddings.init_record_manager") as mock_init_record_manager:
        with patch("create_embeddings.load_data_chunks") as mock_load_data_chunks:
            with patch("create_embeddings.calculate_embedding_cost") as mock_calculate_embedding_cost:
                with patch("create_embeddings.index_chunks") as mock_index_chunks:
                    run_indexing_process(config)
                    mock_init_record_manager.assert_called_once_with(namespace=config.namespace, db_url=config.db_url)
                    mock_load_data_chunks.assert_called_once_with(
                        config.knowledge_base_path, config.chunk_size, config.chunk_overlap
                    )
                    assert mock_calculate_embedding_cost.call_count == 1
                    assert mock_index_chunks.call_count == 1


if __name__ == "__main__":
    pytest.main()
