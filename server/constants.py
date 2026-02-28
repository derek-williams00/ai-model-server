"""Application-wide constants. No functions – values only."""

# --- Provider default base URLs ---
OLLAMA_DEFAULT_BASE_URL: str = "http://localhost:11434"
OPENAI_DEFAULT_BASE_URL: str = "https://api.openai.com/v1"

# --- HTTP client settings ---
PROVIDER_REQUEST_TIMEOUT: int = 120  # seconds

# --- Application metadata ---
APP_TITLE: str = "AI Model Server"
APP_DESCRIPTION: str = "Lightweight OpenAI-compatible LLM proxy server."
APP_VERSION: str = "0.1.0"
