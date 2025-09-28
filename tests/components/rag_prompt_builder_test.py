from haystack.components.builders import PromptBuilder

from src.components.rag_prompt_builder import initialize_rag_prompt_builder


def test_initialize_rag_prompt_builder() -> None:
    """
    Test that initialize_rag_prompt_builder returns a PromptBuilder with correct template content.
    """

    prompt_builder = initialize_rag_prompt_builder()

    expected_template = """You are a helpful and knowledgeable AI assistant named Mona.
    Your task is to answer the user's question based *only* on the provided documents.
    If the documents do not contain the answer, you must state that you cannot answer based on the provided information.
    Do not use any prior knowledge.
  
    Here are the documents:
    {% for doc in documents %}
    <document id="{{ loop.index }}">
      <content>
        {{ doc.content }}
      </content>
      {% if doc.meta %}
      <metadata>
        Document {{ loop.index }}:
        {% for key, value in doc.meta.items() %}
        {{ key }}: {{ value }}
        {% endfor %}
      </metadata>
      {% endif %}
    </document>
    <citation_format>
    When referencing information, use this format:
    - [{{ loop.index }}: {{ doc.meta.title or doc.meta.file_name or "Document " + loop.index|string }}{% if doc.meta.page %}, p.{{ doc.meta.page }}{% endif %}]
    </citation_format>
    {% endfor %}

    Based on the documents above, please answer the following question and cite your sources appropriately after the answer.
    Question: {{ query }}
    Answer:
    """

    assert isinstance(prompt_builder, PromptBuilder)
    assert prompt_builder.template is not None
    assert prompt_builder.to_dict()["init_parameters"]["template"] == expected_template
    assert prompt_builder.to_dict()["init_parameters"]["required_variables"] == [
        "query",
        "documents",
    ]
