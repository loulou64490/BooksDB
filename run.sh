#!/bin/bash

# Define the virtual environment directory
VENV_DIR="venv"

# Check if the virtual environment already exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "Virtual environment created."

    # Activate the virtual environment
    source "$VENV_DIR/bin/activate"

    # Check if requirements.txt exists, then install the requirements
    if [ -f "requirements.txt" ]; then
        echo "Installing dependencies from requirements.txt..."
        pip install -r requirements.txt
        echo "Dependencies installed."
    else
        echo "requirements.txt not found. Please make sure it exists."
        exit 1
    fi
else
    echo "Virtual environment already exists."
    # Activate the virtual environment
    source "$VENV_DIR/bin/activate"
fi

# Run the Flask app
echo "Starting Flask application..."
flask --app BooksDB run --debug &

# Open the application in the default web browser
sleep 1 # Give Flask some time to start
xdg-open http://localhost:5000 2>/dev/null || open http://localhost:5000 2>/dev/null || echo "Please open http://localhost:5000 manually."

# Keep the script running to keep Flask running in the background
wait
