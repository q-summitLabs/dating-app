#!/bin/bash
# start.sh — Start FastAPI server with auto-reload

echo "🚀 Starting FastAPI server on http://0.0.0.0:8080 ..."
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
