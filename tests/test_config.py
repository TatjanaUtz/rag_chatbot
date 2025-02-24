import pytest
from pydantic import ValidationError

from config import ChatbotSettings, IndexingSettings


def test_chatbot_settings_defaults():
    settings = ChatbotSettings()
    assert settings.openai_model == "gpt-4o-mini"
    assert settings.prompt_name == "rlm/rag-prompt"


def test_indexing_settings_defaults():
    settings = IndexingSettings()
    assert settings.knowledge_base_path == "data/raw"
    assert settings.openai_model == "text-embedding-3-large"
    assert settings.collection_name == "3Dfindit"
    assert settings.chunk_size == 1000
    assert settings.chunk_overlap == 200
    assert settings.cleanup == "full"


def test_indexing_settings_computed_fields():
    settings = IndexingSettings(openai_model="test-model", collection_name="test-collection")
    assert settings.vectorstore_path == "vectorstore/test-model"
    assert settings.chroma_path == "vectorstore/test-model/chroma_db"
    assert settings.namespace == "chroma/test-collection"
    assert settings.db_url == "sqlite:///vectorstore/test-model/record_manager_cache.sql"


def test_invalid_chunk_size():
    with pytest.raises(ValidationError):
        IndexingSettings(chunk_size=-1)


def test_invalid_chunk_overlap():
    with pytest.raises(ValidationError):
        IndexingSettings(chunk_overlap=-1)


if __name__ == "__main__":
    pytest.main()
