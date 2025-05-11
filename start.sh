#!/bin/bash

# Change to the correct directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Start the Flask application
python3 app.py 