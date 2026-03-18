#!/bin/bash
set -e  # Exit on error

# Find auth_server directory and run from there
if [ -d "nike-bot-pro/auth_server" ]; then
    cd nike-bot-pro/auth_server
elif [ -d "auth_server" ]; then
    cd auth_server
fi

# Run uvicorn
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}

