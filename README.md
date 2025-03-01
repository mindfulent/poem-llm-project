# Poem Generator LLM Project

![Conceptual Architecture](conceptual_diagram.png)

A project to fine-tune a small LLM using LoRA on Ollama to generate poems based on time, date, and location inputs. The project works with Python 3.12+ and uses Ollama to interface with local LLMs.

## Project Structure

- `data/raw`: Raw poem datasets
- `data/processed`: Processed and formatted data for training
- `src`: Source code for the project
- `scripts`: Utility scripts for data processing and model training
- `venv`: Virtual environment (created during setup)

## Setup

The easiest way to set up the project is to use the included setup script:

```
./setup.sh
```

This script will:
1. Create and activate a virtual environment
2. Install all dependencies from requirements.txt
3. Check if Ollama is installed and running
4. Verify that the required base model (llama3.1:8b) is available
5. Optionally run an integration test

If you prefer to set up manually:

1. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Ensure Ollama is installed with the base model:
```
ollama list
```

## Requirements

- Python 3.12+
- Ollama installed and running
- Base model llama3.1:8b pulled in Ollama

## Usage

Always activate the virtual environment before using the project:
```
source venv/bin/activate
```

1. Process data:
```
python scripts/process_data.py
```

2. Fine-tune model:
```
python scripts/train_model.py
```

3. Generate poems in interactive mode:
```
python src/generate_poem.py --interactive
```

4. Or generate a specific poem:
```
python src/generate_poem.py --model llama3.1:8b --time "18:30" --date "2023-10-21" --location "Paris"
```

## Models

The project works with the following Ollama models:
- llama3.1:8b (recommended base model)
- You can also use any other LLM available in your Ollama installation
- After training, you can create a custom model following the Modelfile template in test_model/

## Testing

Run the integration test to verify your setup:
```
python scripts/test_integration.py
```

This will:
- Check if Ollama is installed and running
- Process a small test dataset
- Create a sample Modelfile
- Generate a test poem

## License

[MIT License](LICENSE)
