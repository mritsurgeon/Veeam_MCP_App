# Development Guide

## Quick Start

### Backend Setup

1. **Create virtual environment**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure API keys**:
```bash
# Create .env file in backend/ directory
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
```

4. **Run the FastAPI server**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Testing

#### Run All Tests
```bash
cd backend
pytest tests/ -v
```

#### Run Test Harness
The test harness validates LLM adapter connections:

```bash
cd backend
python run_tests.py
```

Or with environment variables:
```bash
export OPENAI_API_KEY="your-key"
python run_tests.py
```

#### Run Specific Test Suites
```bash
# Test a specific adapter
pytest tests/test_adapters/test_openai_adapter.py -v

# Test with coverage
pytest tests/ --cov=app --cov-report=html
```

## Architecture Overview

### LLM Adapter System

The adapter system provides a unified interface for multiple LLM providers:

```
BaseLLMAdapter (Abstract)
├── OpenAIAdapter
├── AnthropicAdapter
└── OllamaAdapter
```

All adapters implement:
- `chat()` - Send chat completion requests
- `health_check()` - Validate API connectivity
- `get_capabilities()` - Return provider capabilities
- `normalize_messages()` - Convert unified messages to provider format

### Adding a New Adapter

1. **Create adapter class**:
```python
from app.core.base_adapter import BaseLLMAdapter
from app.core.schemas import LLMConfig, LLMResponse, Message

class NewProviderAdapter(BaseLLMAdapter):
    def _validate_config(self) -> None:
        # Validate provider-specific config
        pass

    async def chat(self, messages, stream=False, **kwargs):
        # Implement chat completion
        pass

    async def health_check(self) -> bool:
        # Implement health check
        pass

    def get_capabilities(self):
        # Return capabilities
        pass
```

2. **Register in factory**:
```python
from app.core.adapter_factory import AdapterFactory
AdapterFactory.register_adapter("newprovider", NewProviderAdapter)
```

### API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/v1/chat` - Chat completion
- `GET /api/v1/providers` - List supported providers
- `GET /api/v1/providers/{provider}/health` - Provider health check

### Configuration

Configuration is loaded from:
1. `config/config.yaml` - YAML configuration file
2. Environment variables (preferred for secrets)
3. Default values

Example API call:
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "model": "gpt-4",
    "stream": false
  }'
```

## Project Structure

```
backend/
├── app/
│   ├── adapters/          # LLM provider adapters
│   ├── api/               # FastAPI routes
│   ├── core/              # Core interfaces and schemas
│   └── main.py            # FastAPI app entry point
├── tests/                 # Test suite
│   ├── test_adapters/     # Adapter tests
│   └── test_harness.py    # Test harness
└── requirements.txt       # Dependencies
```

## Code Style

- Follow PEP 8 for Python code
- Use type hints for all function signatures
- Write docstrings for all classes and functions
- Use `black` for code formatting (optional)
- Use `mypy` for type checking (optional)

## Testing Guidelines

1. **Unit Tests**: Test individual adapter methods in isolation
2. **Integration Tests**: Test adapter connections with mock APIs
3. **Test Harness**: Validate real API connections (requires API keys)

### Mock vs Real Tests

- **Unit tests** use mocks to avoid API calls
- **Test harness** makes real API calls (requires credentials)
- Run test harness before deploying to verify connectivity

## Common Tasks

### Adding a New LLM Provider

1. Install provider SDK: `pip install provider-sdk`
2. Create adapter class inheriting from `BaseLLMAdapter`
3. Implement required methods
4. Register in `AdapterFactory`
5. Add tests
6. Update documentation

### Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or set in environment:
```bash
export LOG_LEVEL=DEBUG
```

### Performance Testing

Use the test harness to measure response times:
```bash
python run_tests.py
```

Check the `response_time` field in results.

## Next Steps

- Phase 2: Implement additional adapters (Grok, Hugging Face)
- Phase 3: Add MCP server integration
- Phase 4: Build frontend UI
- Phase 5: Add artifact rendering and visualization

## Troubleshooting

### Adapter Connection Fails

1. Check API keys are set correctly
2. Verify base URL is correct
3. Check network connectivity
4. Review adapter-specific error messages

### Tests Fail

1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check Python version: `python --version` (should be 3.10+)
3. Verify test environment doesn't require real API calls (use mocks)

