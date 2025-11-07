#!/bin/bash
# start.sh — Start FastAPI server with auto-reload

echo "🚀 Starting FastAPI server on http://127.0.0.1:8080 ..."
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
