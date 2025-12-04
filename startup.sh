#!/bin/bash

# Startup script for Task CLI project
# This script sets up and runs the Django development server on 127.0.0.1:8000

echo "=================================="
echo "Task CLI Server Startup"
echo "=================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
echo "Activating virtual environment..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Error: Virtual environment (.venv) not found!"
    echo "Please create a virtual environment first with: python3 -m venv .venv"
    exit 1
fi

# Navigate to backend directory
echo "Navigating to backend directory..."
cd taskcli_backend

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the development server on 127.0.0.1:8000
export DJANGO_DEBUG=True
echo "=================================="
echo "Starting Django development server on 127.0.0.1:8000"
echo "Press Ctrl+C to stop the server"
echo "=================================="
python manage.py runserver 127.0.0.1:8000
