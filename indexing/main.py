"""Indexing.

This module sets up and runs the indexing process for PDF documents. It includes configuration settings,
initialization of components, and monitoring of file system events to trigger re-indexing.
"""

import logging
import time

from indexing.settings import IndexingSettings
from langchain.indexes import SQLRecordManager, index
from langchain_chroma import Chroma
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Setup config
config = IndexingSettings()
logging.info(f"Indexing settings: {config.model_dump()}")

# Initialize components
try:
    embedding = HuggingFaceEmbeddings(model_name=config.embedding_model_name)
    vectorstore = Chroma(
        collection_name=config.collection_name, embedding_function=embedding, persist_directory=config.chroma_path
    )
    record_manager = SQLRecordManager(config.namespace, db_url=config.db_url)
    record_manager.create_schema()
except Exception as e:
    logging.critical(f"Failed to initialize components: {e}")
    raise


def index_documents() -> None:
    """Index PDF documents by loading them, splitting them into chunks, and storing the chunks in a vectorstore.

    Raises:
        Exception: If an error occurs during the indexing process.
    """
    logging.info("Starting indexing process...")
    try:
        documents = PyPDFDirectoryLoader(config.src_path).load()

        chunks = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap
        ).split_documents(documents)
        res = index(chunks, record_manager, vectorstore, cleanup=config.cleanup, source_id_key="source")
        logging.info(f"Indexing completed: {res}")
    except Exception as e:
        logging.error(f"Error during indexing: {e}")
        raise


class PDFFileEventHandler(FileSystemEventHandler):  # type: ignore
    """
    Event handler for monitoring changes in PDF files. Triggers re-indexing on file modifications, creations, and deletions.
    """

    def on_modified(self, event: FileSystemEvent) -> None:
        """
        Called when a file is modified.

        Args:
            event (FileSystemEvent): The event object containing information about the modified file.
        """
        if event.src_path.endswith(".pdf"):
            logging.info(f"Modified: {event.src_path}")
            index_documents()

    def on_created(self, event: FileSystemEvent) -> None:
        """
        Called when a file is created.

        Args:
            event (FileSystemEvent): The event object containing information about the created file.
        """
        if event.src_path.endswith(".pdf"):
            logging.info(f"Created: {event.src_path}")
            index_documents()

    def on_deleted(self, event: FileSystemEvent) -> None:
        """
        Called when a file is deleted.

        Args:
            event (FileSystemEvent): The event object containing information about the deleted file.
        """
        if event.src_path.endswith(".pdf"):
            logging.info(f"Deleted: {event.src_path}")
            index_documents()


def start_monitoring() -> None:
    """
    Start monitoring the source directory for changes in PDF files and triggers re-indexing accordingly.
    """
    event_handler = PDFFileEventHandler()
    observer = Observer()
    observer.schedule(event_handler, config.src_path, recursive=True)
    observer.start()
    logging.info("Started monitoring for changes in PDF files...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    try:
        index_documents()
        start_monitoring()
    except Exception as e:
        logging.critical(f"Unhandled exception: {e}")
        raise
