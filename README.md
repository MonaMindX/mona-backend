# mona-backend

![Mona Backend Banter](static/images/repo-banter.png)

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3129/)
[![Hayhooks 0.10.1](https://img.shields.io/badge/hayhooks-0.10.1-ff69b4)](https://github.com/MonaMindX/hayhooks)
[![FastAPI 0.116.1](https://img.shields.io/badge/FastAPI-0.116.1-009688.svg)](https://fastapi.tiangolo.com/)
[![Haystack 2.17.1](https://img.shields.io/badge/haystack--ai-2.17.1-orange.svg)](https://github.com/deepset-ai/haystack)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat)](https://pycqa.github.io/isort/)
[![Type checking: mypy](https://img.shields.io/badge/type%20checking-mypy-brightgreen)](https://github.com/python/mypy)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](http://unlicense.org/)
![Status: Active](https://img.shields.io/badge/status-active-success.svg)
[![Made with ❤️](https://img.shields.io/badge/made%20with-❤️-red.svg)](https://github.com/MonaMindX)

## 📑 Table of Contents

- [Overview](#overview)
- [Available Pipelines](#available-pipelines)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [License](#license)
- [Contributing](#contributing)
- [Reporting Issues](#reporting-issues)

## Overview

Mona-backend provides the core API services for the Mona platform.

## Available Pipelines

### Indexing Pipeline (`indexing_mona`)

The Indexing Pipeline (`indexing_mona`) is an automated document processing pipeline designed to convert, split, clean, embed, and store documents in a vector database for intelligent search and retrieval.

**Supported Formats**: `.md`, `.txt`, `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.xls`

#### Indexing Pipeline Flow

The Indexing Pipeline follows a step-by-step process to process and store documents in the vector database. Here's a high-level overview of the pipeline flow:

1. **Document Upload**: Users upload documents to the Mona platform.
2. **Document Conversion**: The pipeline converts the uploaded documents to Markdown format.
3. **Document Processing & Chunking**: The pipeline processes and splits the Markdown documents into smaller chunks.
4. **Document Embedding**: The pipeline generates embeddings for each chunk of the document using a pre-trained embedding model.
5. **Document Storage**: The pipeline stores the document embeddings and associated metadata in a vector database for efficient search and retrieval.
6. **Document Cleanup**: The pipeline removes any temporary files or intermediate artifacts created during the processing and storage of the documents.

### Retrieval Pipeline (`retrieval_mona`)

The Retrieval Pipeline (`retrieval_mona`) is an intelligent document search and retrieval system that finds the most relevant documents from the vector database based on user queries using semantic similarity.

**Input**: Natural language queries (text strings)

#### Retrieval Pipeline Flow

The Retrieval Pipeline follows a streamlined process to find and return relevant documents. Here's a high-level overview of the pipeline flow:

1. **Query Processing**: Users submit natural language queries to search for relevant documents.
2. **Query Embedding**: The pipeline generates embeddings for the input query using the same embedding model used during indexing.
3. **Similarity Search**: The pipeline performs semantic similarity search against the vector database to find the most relevant document chunks.
4. **Document Retrieval**: The pipeline retrieves the top matching documents with their associated metadata and relevance scores.
5. **Response Formatting**: The pipeline formats and returns the retrieved documents as a structured response.

### Query Processing Pipeline (`mona`)

The Query Processing Pipeline (`mona`) is the main conversational AI pipeline that intelligently processes user queries and generates contextually appropriate responses. It combines direct question answering with retrieval-augmented generation (RAG) to provide accurate and relevant answers.

**Input**: Natural language queries (text strings)
**Output**: Generated text responses

#### Query Processing Pipeline Flow

The Query Processing Pipeline uses intelligent routing to determine the best approach for answering each query. Here's a high-level overview of the pipeline flow:

1. **Query Classification**: The pipeline analyzes the incoming query to determine whether it requires document retrieval or can be answered directly.

2. **Intelligent Routing**: Based on the classification results, the pipeline routes the query through one of two paths:
   - **Direct Path**: For general questions that don't require specific document context
   - **RAG Path**: For queries that need information from the knowledge base

3. **Direct Query Processing**:
   - Builds a direct prompt for general knowledge questions
   - Sends the prompt directly to the LLM generator

4. **RAG Query Processing**:
   - Generates embeddings for the query using the same model used during indexing
   - Retrieves relevant documents from the vector database
   - Builds a context-aware prompt with retrieved documents
   - Combines query and retrieved context for enhanced responses

5. **Prompt Joining**: The pipeline merges outputs from both prompt builders using a branch joiner to ensure only the appropriate prompt reaches the LLM.

6. **Response Generation**: A single LLM generator processes the final prompt and generates the response, ensuring consistent output quality regardless of the routing path.

7. **Response Delivery**: The pipeline returns the generated response to the user, with support for both synchronous and streaming modes.

## Getting Started

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/MonaMindX/mona-backend.git
   cd mona-backend
   ```

2. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -e .
   ```

   For development:

   ```bash
   pip install -e ".[dev,test]"
   ```

4. Run the development server:

   ```bash
   python -m src.main
   ```

### Configuration

The application is configured using environment variables. Create a `.env` file in the project root by copying the example file:

```bash
cp .env.example .env
```

Then, update the .env file with your specific settings.

## API Endpoints

### API Documentation

When the server is running, you can access the interactive API documentation:

- Swagger UI: `http://localhost:1416/docs`
- ReDoc: `http://localhost:1416/redoc`

### Pipelines routes

| Method | Endpoint              | Description                       | Content Type          |
| ------ | --------------------- | --------------------------------- | --------------------- |
| POST   | `/indexing_mona/run`  | Run the Indexing Pipeline         | `multipart/form-data` |
| POST   | `/retrieval_mona/run` | Run the Retrieval Pipeline        | `application/json`    |
| POST   | `/mona/run`           | Run the Query Processing Pipeline | `application/json`    |

#### Indexing Pipeline Parameters

**Required Parameters:**

- `files` (array): List of file upload objects containing document data
- `titles` (array of strings): List of titles for each document (must match number of files)

**Optional Parameters:**

- `summaries` (array of strings): List of summaries for each document
- `document_types` (array of strings): List of document types for each document

**Example Usage:**

```bash
curl -X POST "http://localhost:1416/indexing_mona/run" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document1.pdf" \
  -F "files=@document2.docx" \
  -F "titles=Technical Documentation" \
  -F "titles=User Manual" \
  -F "summaries=API reference guide" \
  -F "summaries=End-user instructions" \
  -F "document_types=technical" \
  -F "document_types=manual"
```

**Response:**

```json
"Successfully added 2 documents to the knowledgebase."
```

#### Retrieval Pipeline Parameters

**Required Parameters:**

- `query` (string): Natural language query string for document retrieval

**Example Usage:**

```bash
curl -X POST "http://localhost:1416/retrieval_mona/run" \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I set up the API?"}'
```

**Response:**

```json
[
  {
    "id": "doc_123",
    "content": "To configure API settings, navigate to the configuration file...",
    "meta": {
      "file_name": "api_guide.pdf",
      "title": "API Configuration Guide",
      "document_type": "technical",
      "summary": "Complete guide for API setup"
    },
    "score": 0.95
  },
  {
    "id": "doc_456",
    "content": "API configuration involves setting environment variables...",
    "meta": {
      "file_name": "setup_manual.docx",
      "title": "Setup Manual",
      "document_type": "manual",
      "summary": "Installation and setup instructions"
    },
    "score": 0.87
  }
]
```

#### Query Processing Pipeline Parameters

**Required Parameters:**

- `query` (string): Natural language query string for document retrieval

**Example Usage:**

```bash
curl -X POST "http://localhost:1416/mona/run" \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I set up the API?"}'
```

**Response:**

```json
"Here's how you can set up the API: [generated response content]"
```

### System Routes

| Method | Endpoint         | Description                                    |
| ------ | ---------------- | ---------------------------------------------- |
| GET    | `/api/v1/health` | Comprehensive health check with system metrics |
| GET    | `/api/v1/ready`  | Kubernetes readiness probe                     |
| GET    | `/api/v1/live`   | Kubernetes liveness probe                      |
| GET    | `/api/v1/info`   | System information and environment details     |

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src
```

## Code Quality

This project maintains high code quality standards using:

- **Black**: Code formatting with 88 character line length
- **isort**: Import sorting with Black compatibility
- **mypy**: Static type checking with strict settings
- **bandit**: Security vulnerability scanning
- **pytest**: Testing framework with asyncio support

## License

This project is released under the [Unlicense](https://unlicense.org/), which dedicates the work to the public domain. This means you can copy, modify, publish, use, compile, sell, or distribute this software, for any purpose, commercial or non-commercial, and by any means, without asking permission.

For more information, see the [LICENSE](LICENSE) file in the repository.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Ensure you have run the code quality tools before submitting:

   ```bash
   black .
   isort .
   mypy .
   bandit -r src
   ```

2. Make sure all tests pass:

   ```bash
   pytest
   ```

3. Update documentation as needed.

4. Create a clear, concise PR with a description of the changes and their purpose.

## Reporting Issues

If you find a bug or have a feature request, please open an issue on the GitHub repository. Include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected and actual behavior
- Screenshots if applicable
- Any relevant logs or error messages
