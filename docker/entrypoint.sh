#!/bin/bash

uv run python src/cli.py database drop-collections
uv run python src/cli.py database create-indexes

uv run python src/cli.py pipeline run-pipeline

uv run uvicorn src.infrastructure.api.app:app --host 0.0.0.0 --port 8000