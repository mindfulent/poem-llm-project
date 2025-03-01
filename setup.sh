#!/bin/bash

# Setup script for Poem Generator LLM Project
echo "Setting up the Poem Generator LLM Project..."

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if Ollama is installed
if command -v ollama >/dev/null 2>&1; then
    echo "Ollama is installed."
    
    # Check if Ollama is running
    if ollama list >/dev/null 2>&1; then
        echo "Ollama is running."
        
        # Check if the required model is available
        if ollama list | grep -q "llama3.1:8b"; then
            echo "The required base model (llama3.1:8b) is available."
        else
            echo "The required base model (llama3.1:8b) is not available."
            echo "Do you want to pull it now? (y/n)"
            read answer
            if [ "$answer" = "y" ]; then
                echo "Pulling llama3.1:8b..."
                ollama pull llama3.1:8b
            else
                echo "Please pull a base model before training."
                echo "You can pull it later using: ollama pull llama3.1:8b"
            fi
        fi
    else
        echo "Ollama is installed but not running."
        echo "Please start Ollama before proceeding."
    fi
else
    echo "Ollama is not installed."
    echo "Please install Ollama from https://ollama.ai/ before proceeding."
fi

# Run integration test
echo "Do you want to run the integration test? (y/n)"
read answer
if [ "$answer" = "y" ]; then
    echo "Running integration test..."
    python scripts/test_integration.py
fi

echo "Setup completed!"
echo "To activate the virtual environment in the future, run: source venv/bin/activate"
echo "To run the data processing script: python scripts/process_data.py"
echo "To train the model: python scripts/train_model.py"
echo "To generate poems: python src/generate_poem.py --interactive"
