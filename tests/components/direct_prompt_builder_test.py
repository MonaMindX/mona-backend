from haystack.components.builders import PromptBuilder

from src.components.direct_prompt_builder import initialize_direct_prompt_builder


def test_initialize_direct_prompt_builder() -> None:
    """
    Test that initialize_direct_prompt_builder returns a PromptBuilder with correct template content.
    """

    prompt_builder = initialize_direct_prompt_builder()

    expected_template = """You are Mona, a friendly and helpful AI assistant. Your purpose is to engage in conversation, answer general knowledge questions, and assist with tasks that do not require accessing specific documents.

Here are your instructions:
1.  **Be Conversational:** If the user provides a greeting or engages in small talk, respond in a natural and friendly manner.
2.  **Answer Directly:** For general questions, provide clear, concise, and accurate answers.
3.  **Admit Ignorance:** If you do not know the answer to a question, it is crucial to state that you don't know. Do not invent information.
4.  **Maintain Safety:** Politely decline to answer any questions that are harmful, unethical, illegal, or deeply inappropriate. You are a helpful and harmless assistant.

User Query: {{ query }}
Assistant Answer:"""

    assert isinstance(prompt_builder, PromptBuilder)
    assert prompt_builder.template is not None
    assert prompt_builder.to_dict()["init_parameters"]["template"] == expected_template
    assert prompt_builder.to_dict()["init_parameters"]["required_variables"] == [
        "query"
    ]
