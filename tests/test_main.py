from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

from main import State, generate_answer, generate_response, initialize_llm, load_prompt, retrieve_documents


# Mock configurations
class MockConfig:
    openai_model = "gpt-3.5-turbo"
    prompt_name = "default-prompt"
    num_context_sources = 3  # Added to match the config in the main code


config = MockConfig()

# Mock data
mock_question = "What is the capital of France?"
mock_documents = [
    Document(page_content="Paris is the capital of France.", metadata={"source": "example.pdf", "page": 3})
]
mock_state = State(question=mock_question, num_references=3, context=mock_documents, answer="")


# Test initialize_llm
def test_initialize_llm():
    with patch("main.ChatOpenAI") as MockChatOpenAI:
        mock_llm = MagicMock()
        MockChatOpenAI.return_value = mock_llm
        llm = initialize_llm(config.openai_model)
        MockChatOpenAI.assert_called_once_with(model=config.openai_model)
        assert llm == mock_llm


# Test load_prompt
def test_load_prompt():
    with patch("main.hub.pull") as mock_pull:
        mock_prompt = MagicMock()
        mock_pull.return_value = mock_prompt
        prompt = load_prompt(config.prompt_name)
        mock_pull.assert_called_once_with(config.prompt_name)
        assert prompt == mock_prompt


# Test retrieve_documents
def test_retrieve_documents():
    with patch("main.vectorstore.similarity_search") as mock_search:
        mock_search.return_value = mock_documents
        result = retrieve_documents(mock_state)
        mock_search.assert_called_once_with(mock_question, mock_state["num_references"])
        assert result == {"context": mock_documents}


# Test retrieve_documents with error
def test_retrieve_documents_error():
    with patch("main.vectorstore.similarity_search", side_effect=Exception("Error")):
        result = retrieve_documents(mock_state)
        assert result == {"context": []}


# Test generate_answer
def test_generate_answer():
    with patch("main.prompt") as mock_prompt, patch("main.llm") as mock_llm:
        mock_prompt.invoke.return_value = {"question": mock_question, "context": "Paris is the capital of France."}
        mock_llm.invoke.return_value = MagicMock(content="Paris")
        result = generate_answer(mock_state)
        assert result == {"answer": "Paris"}


# Test generate_answer with error
def test_generate_answer_error():
    with patch("main.prompt") as mock_prompt, patch("main.llm") as mock_llm:
        mock_prompt.invoke.side_effect = Exception("Error")
        mock_llm.invoke.side_effect = Exception("Error")
        result = generate_answer(mock_state)
        assert result == {"answer": "An error occurred while generating the answer."}


# Test generate_response
def test_generate_response():
    with patch("main.graph.invoke") as mock_graph_invoke:
        mock_graph_invoke.return_value = {
            "answer": "Paris",
            "context": mock_documents * 3,
        }
        response, *sources = generate_response(mock_question, [], 3)
        assert response == "Paris"
        assert len(sources) == 10


if __name__ == "__main__":
    pytest.main()
