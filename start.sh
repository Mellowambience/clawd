#!/usr/bin/env bash
# start.sh - MIST local startup
# Usage: chmod +x start.sh && ./start.sh

set -e

echo "MIST Sovereign Gateway starting..."

if [ -f .env ]; then
  set -a
  source .env
  set +a
  echo ".env loaded"
fi

export PYTHONPATH="$(pwd):${PYTHONPATH}"

if command -v ollama &>/dev/null; then
  if ! pgrep -x ollama >/dev/null; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 2
  else
    echo "Ollama already running"
  fi
else
  echo "Ollama not found - will use Gemini fallback (GEMINI_API_KEY required)"
fi

echo "Starting MIST gateway on port 18789..."
python -m uvicorn gateway.server:app --host 0.0.0.0 --port 18789 --reload
