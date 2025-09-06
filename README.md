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
- [Getting Started](#getting-started)
  - [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [License](#license)
- [Contributing](#contributing)
  - [Reporting Issues](#reporting-issues)

## Overview

Mona-backend provides the core API services for the Mona platform.

Mona-backend is the core backend service of the MonaMind project.

## Getting Started

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/MonaMindX/mona-backend.git
   cd mona-backend
   ```

2. Install dependencies:

   ```bash
   pip install -e .
   ```

   For development:

   ```bash
   pip install -e ".[dev,test]"
   ```

3. Run the development server:

   ```bash
   python -m src.main
   ```

### Configuration

The application is configured using environment variables. Create a `.env` file in the project root by copying the example file:

```bash
cp .env.example .env
```

Then, update the .env file with your specific settings. The following variables are available:

| Variable        | Description                                                               | Default       |
| --------------- | ------------------------------------------------------------------------- | ------------- |
| `ENVIRONMENT`   | The runtime environment. Can be `development`, `production`, or `test`.   | `development` |
| `HAYHOOKS_HOST` | The host for the Hayhooks server.                                         | `localhost`   |
| `HAYHOOKS_PORT` | The port for the Hayhooks server.                                         | `1416`        |
| `LOG`           | Logging level. Can be `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`. | `INFO`        |

## API Endpoints

### System Routes

| Method | Endpoint         | Description                                    |
| ------ | ---------------- | ---------------------------------------------- |
| GET    | `/api/v1/health` | Comprehensive health check with system metrics |
| GET    | `/api/v1/ready`  | Kubernetes readiness probe                     |
| GET    | `/api/v1/live`   | Kubernetes liveness probe                      |
| GET    | `/api/v1/info`   | System information and environment details     |

## API Documentation

When the server is running, you can access the interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

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

### Reporting Issues

If you find a bug or have a feature request, please open an issue on the GitHub repository. Include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected and actual behavior
- Screenshots if applicable
- Any relevant logs or error messages
