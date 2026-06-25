#!/bin/bash

echo "==========================================="
echo "  Starting ArrowMilka Server"
echo "==========================================="

# Activate virtual environment if exists
if [ -d ".venv" ]; then
    echo "Activating Virtual Environment..."
    source .venv/bin/activate
else
    echo "[WARNING] .venv not found. Running with system python..."
fi

echo "Starting FastAPI server..."

nohup uvicorn main:app --host 0.0.0.0 --port 8600 --reload
#uvicorn app.main --host 0.0.0.0 --port 8600 --reload

echo ""
echo "Server stopped."
