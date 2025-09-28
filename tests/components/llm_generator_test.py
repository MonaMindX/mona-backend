from haystack.components.generators import OpenAIGenerator

from src.components.llm_generator import initialize_llm_generator
from src.config.settings import settings


def test_initialize_llm_generator_with_default_parameters() -> None:
    """
    Test that initialize_llm_generator returns an OpenAIGenerator instance with default parameters.
    """

    generator = initialize_llm_generator()
    print(generator.to_dict()["init_parameters"])

    assert isinstance(generator, OpenAIGenerator)
    assert (
        generator.to_dict()["init_parameters"]["api_base_url"]
        == settings.openai_api_base_url
    )
    assert generator.to_dict()["init_parameters"]["model"] == settings.llm_model
    assert generator.generation_kwargs["temperature"] == settings.llm_temperature
    assert generator.generation_kwargs["max_tokens"] == settings.llm_max_tokens
    assert generator.generation_kwargs["max_tokens"] == settings.llm_max_tokens


def test_initialize_llm_generator_custom_api_base_url() -> None:
    """
    Test that initialize_llm_generator accepts custom api_base_url parameter and passes it to OpenAIGenerator.
    """
    custom_api_base_url = "openai.com/v1"

    generator = initialize_llm_generator(api_base_url=custom_api_base_url)

    assert generator.to_dict()["init_parameters"]["api_base_url"] == custom_api_base_url


def test_initialize_llm_generator_with_custom_model() -> None:
    """
    Test that initialize_llm_generator accepts custom model parameter and passes it to OpenAIGenerator.
    """
    custom_model = "gpt-4-custom"

    generator = initialize_llm_generator(model=custom_model)

    assert generator.to_dict()["init_parameters"]["model"] == custom_model


def test_initialize_llm_generator_custom_temperature() -> None:
    """
    Test that initialize_llm_generator accepts custom temperature parameter and includes it in generation_kwargs.
    """
    custom_temperature = 0.8

    generator = initialize_llm_generator(temperature=custom_temperature)

    assert generator.generation_kwargs["temperature"] == custom_temperature


def test_initialize_llm_generator_with_custom_max_tokens() -> None:
    """
    Test that initialize_llm_generator accepts custom max_tokens parameter and includes it in generation_kwargs.
    """
    custom_max_tokens = 2048

    generator = initialize_llm_generator(max_tokens=custom_max_tokens)

    assert generator.generation_kwargs["max_tokens"] == custom_max_tokens
