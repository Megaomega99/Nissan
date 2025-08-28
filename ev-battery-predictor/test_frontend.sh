#!/bin/bash

echo "Testing EV Battery Predictor Frontend..."

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Start the frontend development server
echo "Starting frontend development server..."
cd frontend
npm start
