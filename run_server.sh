#!/usr/bin/env bash
set -e

# Run Paytm VyapaarAI Backend Service
export PYTHONPATH=backend
exec backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
