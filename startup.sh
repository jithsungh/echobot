#!/bin/bash

# Azure App Service startup script for Python Bot Framework
echo "Starting Azure Bot Service..."

# Ensure all environment variables are set
if [ -z "$MicrosoftAppId" ]; then
    echo "WARNING: MicrosoftAppId is not set"
fi

if [ -z "$MicrosoftAppPassword" ]; then
    echo "WARNING: MicrosoftAppPassword is not set"
fi

if [ -z "$MicrosoftAppTenantId" ]; then
    echo "WARNING: MicrosoftAppTenantId is not set"
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start the bot application using Gunicorn
echo "Starting bot with Gunicorn..."
exec gunicorn --bind 0.0.0.0:$PORT --worker-class aiohttp.worker.GunicornWebWorker --workers 1 --timeout 600 --keep-alive 2 --max-requests 1000 app:APP
