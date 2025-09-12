"""
The Document Cleaner removes extra whitespaces, empty lines, specified substrings, regexes
preparing the documents for further processing by LLMs.
"""

from haystack.components.preprocessors import DocumentCleaner


def initialize_document_cleaner() -> DocumentCleaner:
    """
    Initialize the DocumentCleaner component.
    """
    return DocumentCleaner()
