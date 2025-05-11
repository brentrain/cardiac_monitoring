#!/bin/bash

# Change to the correct directory
cd "$(dirname "$0")"

# Check if PID file exists
if [ -f logs/app.pid ]; then
    PID=$(cat logs/app.pid)
    if ps -p $PID > /dev/null; then
        echo "Stopping application (PID: $PID)..."
        kill $PID
        rm logs/app.pid
        echo "Application stopped."
    else
        echo "Application is not running."
        rm logs/app.pid
    fi
else
    echo "No PID file found. Application may not be running."
fi 