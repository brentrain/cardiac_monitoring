#!/bin/bash

# Change to the correct directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the Flask application in the background with port 5001
nohup python3 -c "from app import app; app.run(port=5001)" > logs/app.log 2>&1 &

# Save the process ID
echo $! > logs/app.pid

echo "Application started in background on port 5001. Check logs/app.log for output."
echo "Process ID: $(cat logs/app.pid)" 