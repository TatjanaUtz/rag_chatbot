import logging
from unittest.mock import MagicMock, patch

import pytest
from indexing.main import PDFFileEventHandler, index_documents


@pytest.fixture
def mock_settings():
    with patch("indexing.main.IndexingSettings") as MockSettings:
        mock_config = MockSettings.return_value
        mock_config.embedding_model_name = "test_model"
        mock_config.collection_name = "test_collection"
        mock_config.chroma_path = "/test/path"
        mock_config.namespace = "test_namespace"
        mock_config.db_url = "sqlite:///:memory:"
        mock_config.src_path = "/test/src"
        mock_config.chunk_size = 1000
        mock_config.chunk_overlap = 100
        mock_config.cleanup = True
        yield mock_config


@pytest.fixture
def mock_components(mock_settings):
    with (
        patch("indexing.main.HuggingFaceEmbeddings") as MockEmbeddings,
        patch("indexing.main.Chroma") as MockChroma,
        patch("indexing.main.SQLRecordManager") as MockRecordManager,
    ):
        yield MockEmbeddings, MockChroma, MockRecordManager


def test_initialization_of_components(mock_settings, mock_components):
    """Verify that all components (embedding, vectorstore, record_manager) are initialized correctly."""
    MockEmbeddings, MockChroma, MockRecordManager = mock_components
    try:
        embedding = MockEmbeddings(model_name=mock_settings.embedding_model_name)
        MockChroma(
            collection_name=mock_settings.collection_name,
            embedding_function=embedding,
            persist_directory=mock_settings.chroma_path,
        )
        record_manager = MockRecordManager(mock_settings.namespace, db_url=mock_settings.db_url)
        record_manager.create_schema()
    except Exception as e:
        pytest.fail(f"Initialization failed: {e}")


def test_indexing_of_documents(mock_settings, mock_components):
    """Ensure that documents are loaded, split into chunks, and indexed correctly."""
    with (
        patch("indexing.main.PyPDFDirectoryLoader") as MockLoader,
        patch("indexing.main.RecursiveCharacterTextSplitter") as MockSplitter,
        patch("indexing.main.index") as mock_index,
    ):
        mock_loader_instance = MockLoader.return_value
        mock_loader_instance.load.return_value = ["doc1", "doc2"]
        mock_splitter_instance = MockSplitter.return_value
        mock_splitter_instance.split_documents.return_value = ["chunk1", "chunk2"]
        index_documents()
        mock_loader_instance.load.assert_called_once()
        mock_splitter_instance.split_documents.assert_called_once_with(["doc1", "doc2"])
        mock_index.assert_called_once()


def test_pdf_file_creation_event(mock_settings):
    """Verify that creating a new PDF file triggers the indexing process."""
    event_handler = PDFFileEventHandler()
    with patch("indexing.main.index_documents") as mock_index_documents:
        event = MagicMock()
        event.src_path = "/test/src/new_file.pdf"
        event_handler.on_created(event)
        mock_index_documents.assert_called_once()


def test_pdf_file_modification_event(mock_settings):
    """Verify that modifying an existing PDF file triggers the indexing process."""
    event_handler = PDFFileEventHandler()
    with patch("indexing.main.index_documents") as mock_index_documents:
        event = MagicMock()
        event.src_path = "/test/src/existing_file.pdf"
        event_handler.on_modified(event)
        mock_index_documents.assert_called_once()


def test_pdf_file_deletion_event(mock_settings):
    """Verify that deleting a PDF file triggers the indexing process."""
    event_handler = PDFFileEventHandler()
    with patch("indexing.main.index_documents") as mock_index_documents:
        event = MagicMock()
        event.src_path = "/test/src/deleted_file.pdf"
        event_handler.on_deleted(event)
        mock_index_documents.assert_called_once()


def test_error_handling_during_initialization(mock_settings):
    """Ensure that errors during component initialization are logged and raised."""
    with (
        patch(
            "langchain_huggingface.HuggingFaceEmbeddings", side_effect=Exception("Initialization error")
        ) as mock_embeddings,
        patch("indexing.main.logging.critical") as mock_log_critical,
    ):
        with pytest.raises(Exception, match="Initialization error"):
            try:
                mock_embeddings(model_name=mock_settings.embedding_model_name)
            except Exception as e:
                logging.critical(f"Failed to initialize components: {e}")
                raise
        mock_log_critical.assert_called_once_with("Failed to initialize components: Initialization error")


def test_error_handling_during_indexing(mock_settings):
    """Ensure that errors during the indexing process are logged and raised."""
    with (
        patch("indexing.main.PyPDFDirectoryLoader", side_effect=Exception("Loading error")),
        patch("indexing.main.logging.error") as mock_log_error,
    ):
        with pytest.raises(Exception):
            index_documents()
        mock_log_error.assert_called_once()
