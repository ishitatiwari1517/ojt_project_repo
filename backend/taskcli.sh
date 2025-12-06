#!/bin/bash
# TaskCLI - Interactive Task Manager
# Simple launcher script

cd "$(dirname "$0")/taskcli_backend"

# Activate virtual environment if exists
if [ -d "../.venv" ]; then
    source ../.venv/bin/activate
fi

echo ""
echo "🚀 Launching Task CLI..."
echo ""

python3 manage.py task_cli --interactive
