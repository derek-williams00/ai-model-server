# ai-model-server

A lightweight, OpenAI-compatible LLM proxy server for small-scale personal use.
Routes requests to local (Ollama) or remote (OpenAI-compatible) LLM providers based on a
simple YAML configuration file.

---

## Features

- **OpenAI-compatible API** – drop-in replacement for existing LLM providers
  - `POST /v1/chat/completions`
  - `POST /v1/completions`
  - `GET  /v1/models`
- **Model routing** – map friendly aliases to local or remote providers via YAML config
- **Provider support** – Ollama (local) and OpenAI / OpenAI-compatible APIs (remote)
- **Rate limiting / quotas** – per-model `requests_per_minute` and `daily_token_limit`
- **Structured logging** – request metadata, routing decisions, token usage, errors
- **Web dashboard** – minimal browser UI for health checks, model listing, and chat testing
- **Secure secrets** – API keys loaded from `.env`, never stored in source code

---

## Project Structure

```
.
├── server/
│   ├── api/             # FastAPI route handlers (chat, completions, models)
│   ├── config/          # Pydantic config models + YAML loader
│   ├── dashboard/       # Minimal HTML dashboard
│   ├── providers/       # Provider implementations (Ollama, OpenAI)
│   ├── dependencies.py  # Shared FastAPI dependencies
│   ├── logging_utils.py # Structured logging helpers
│   ├── main.py          # Application entry point
│   └── rate_limiter.py  # In-memory quota tracker
├── tests/               # pytest test suite
├── config.example.yaml  # Example configuration file
├── .env.example         # Environment variable template
└── requirements.txt
```

---

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/derek-williams00/ai-model-server.git
cd ai-model-server
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your OPENAI_API_KEY (and any other variables)
```

### 3. Create a configuration file

```bash
cp config.example.yaml config.yaml
# Edit config.yaml to define your models and providers
```

Example `config.yaml`:

```yaml
models:
  local-small:
    provider: ollama
    model: llama3

  cloud-large:
    provider: openai
    model: gpt-4
    rate_limits:
      daily_token_limit: 50000
      requests_per_minute: 20

log_level: INFO
host: "0.0.0.0"
port: 8000
```

### 4. Start the server

```bash
python -m server.main
# or
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

---

## API Usage

### List available models

```bash
curl http://localhost:8000/v1/models
```

### Chat completion

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local-small",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Text completion

```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "local-small", "prompt": "Once upon a time"}'
```

---

## Web Dashboard

Open `http://localhost:8000` in your browser to:

- Verify the server is running
- See all configured models
- Send a test chat message

---

## Configuration Reference

| Field | Type | Description |
|-------|------|-------------|
| `models.<alias>.provider` | `ollama` \| `openai` | Provider type |
| `models.<alias>.model` | string | Backend model name |
| `models.<alias>.api_base` | string (optional) | Override provider base URL |
| `models.<alias>.rate_limits.daily_token_limit` | int (optional) | Max tokens per day |
| `models.<alias>.rate_limits.requests_per_minute` | int (optional) | Max requests per minute |
| `log_level` | string | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `host` | string | Bind address (default: `0.0.0.0`) |
| `port` | int | Port (default: `8000`) |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI (or compatible) API key |
| `OPENAI_API_BASE` | Override OpenAI base URL (e.g. Azure) |
| `OLLAMA_BASE_URL` | Override Ollama base URL (default: `http://localhost:11434`) |
| `CONFIG_PATH` | Path to YAML config file (default: `./config.yaml`) |

---

## Adding a New Provider

1. Create `server/providers/myprovider.py` subclassing `BaseProvider`
2. Implement `chat_completions()` and `completions()` methods
3. Register the provider in `server/providers/__init__.py`

---

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```

---

## Security Notes

- Never commit `.env` or any file containing API keys (`.env` is in `.gitignore`)
- The server is intended for personal/local use; add authentication middleware before exposing it publicly
