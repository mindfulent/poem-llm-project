# Poem Generator LLM Project

![Conceptual Architecture](conceptual_diagram.png)

A project to fine-tune a small LLM using LoRA on Ollama to generate poems based on time, date, and location inputs. The project works with Python 3.12+ and uses Ollama to interface with local LLMs.

## Project Overview

This project enables the generation of contextually aware poems by:
1. Creating a synthetic dataset of poems with time, date, and location metadata
2. Processing this data into an instruction-tuning format
3. Fine-tuning a Language Model using LoRA (Low-Rank Adaptation)
4. Creating an Ollama model for poem generation
5. Providing a user-friendly interface for generating poems

The generated poems take into account contextual factors like time of day, season, and location to create more relevant and atmospheric poetry.

## Project Structure

- `data/raw`: Raw poem datasets (synthetic_poems.json, test_poems.json)
- `data/processed`: Processed and formatted data for training (training_data.json, train.json, val.json)
- `src`: Source code for the project (generate_poem.py)
- `scripts`: Utility scripts for data processing and model training
  - `process_data.py`: Creates and processes synthetic poem data
  - `train_model.py`: Fine-tunes model using LoRA
  - `test_integration.py`: Tests the complete pipeline
  - `test_data_process.py`: Created during testing for small dataset generation
- `test_model`: Contains template Modelfile for Ollama integration
- `poem-app`: Web application for generating poems
  - `server.js`: Express server with API endpoints
  - `services/`: Backend services for Ollama integration
  - `public/`: Frontend files (HTML, CSS, JavaScript)
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
- Required libraries (detailed in requirements.txt):
  - PEFT and transformers for fine-tuning
  - PyTorch for ML backend
  - Datasets for data management
  - Ollama-python for API integration
  - Astral for sun position calculations

## Data Pipeline

The data processing pipeline (`process_data.py`) performs the following steps:

1. Generates a synthetic dataset of 500 poems with metadata
2. Assigns appropriate themes based on time of day and season
3. Formats data for instruction tuning with diverse prompts
4. Creates train/validation splits (90%/10%)

The dataset includes:
- Time and date information
- Location names
- Time of day classification (morning, day, evening, night)
- Seasonal context (spring, summer, autumn, winter)
- Thematic elements appropriate to the context

## Model Training

The training script (`train_model.py`) handles:

1. Model preparation by mapping Ollama models to HuggingFace equivalents
2. LoRA configuration for efficient fine-tuning
3. Fine-tuning using HuggingFace Trainer API
4. Saving LoRA weights
5. Creating a Modelfile for Ollama integration

LoRA Configuration:
- Default rank (r): 8
- Default alpha: 16
- Default dropout: 0.1
- Target modules: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj

## Usage

Always activate the virtual environment before using the project:
```
source venv/bin/activate
```

1. Process data:
```
python scripts/process_data.py
```

2. Fine-tune model (with default parameters):
```
python scripts/train_model.py
```

   Or with custom parameters:
```
python scripts/train_model.py --base_model llama3.1:8b --output_dir ./lora_model --batch_size 4 --epochs 3 --learning_rate 2e-4
```

3. Generate poems in interactive mode:
```
python src/generate_poem.py --interactive
```

4. Or generate a specific poem:
```
python src/generate_poem.py --model llama3.1:8b --time "18:30" --date "2023-10-21" --location "Paris" --temperature 0.7
```

## Web Application

The project includes a web application in the `poem-app` directory that provides a user-friendly interface for generating poems based on the user's location and current time.

### Features

- Automatically detects the user's location (with permission)
- Generates poems based on location, time of day, and date
- Refreshes the poem every minute
- Responsive design for mobile and desktop
- Accessibility features for screen readers and keyboard navigation

### Running the Web Application

1. Navigate to the poem-app directory:
```
cd poem-app
```

2. Install dependencies:
```
npm install
```

3. Make sure Ollama is running with the poem-generator model:
```
ollama run poem-generator
```

4. Start the server:
```
node server.js
```

5. Open your browser and navigate to:
```
http://localhost:3000
```

### Configuration

You can modify the following settings in the `.env` file:

```
# Server configuration
PORT=3000

# Ollama configuration
OLLAMA_API_URL=http://localhost:11434
MODEL_NAME=poem-generator

# Rate limiting
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=60
```

### Troubleshooting Common Issues

1. **429 Too Many Requests Error**
   - This can occur if the rate limit is too restrictive
   - Increase the `RATE_LIMIT_MAX_REQUESTS` value in the `.env` file
   - Default is now set to 60 requests per minute

2. **Ollama Connection Issues**
   - Ensure Ollama is running: `ollama list`
   - Verify the correct API URL in `.env`: `OLLAMA_API_URL=http://localhost:11434`
   - Make sure the poem-generator model is available: `ollama run poem-generator`

3. **JavaScript Errors**
   - Check the browser console for any errors
   - The application uses modern JavaScript features, ensure you're using an up-to-date browser

## Poem Generation

The generation script (`generate_poem.py`) works by:

1. Taking time, date, location, and temperature inputs
2. Extracting contextual information:
   - Time of day (morning, afternoon, evening, night)
   - Season (spring, summer, autumn, winter)
   - Attempting to get sun position information
3. Creating a prompt with this context
4. Using the Ollama API to generate a poem
5. Providing both interactive and command-line modes

The context extraction enhances poem quality by providing relevant atmospheric details to the model.

## Examples

Here are some examples of poems generated by the fine-tuned model:

![Example Poem Generation 1](poem-app/gen1.png)

![Example Poem Generation 2](poem-app/gen2.png)

### Example 1: Morning in Reno

**Input:** 9:57 AM, Sat Mar 1, Reno NV

**Output:**
```
"Desert Dawn's Gentle Hush"

In Reno's morning light, where Truckee's river flows,
A new day stirs, with Sierra's snowy glows.
At 9:57, the sun ascends to greet the day,
With warmth that whispers through the desert's way.

The High Desert's silence breaks, as dawn's sweet song
Echoes through the streets, where neon lights are strong.
The aroma of coffee wafts, a morning treat,
As gamblers and dreamers rise, their spirits to greet.

The mountains stand sentinel, a rugged, rocky shore,
Where snow-capped peaks meet skyward, evermore.
The Truckee River's gentle voice, a soothing melody plays,
As Reno awakens, to seize the day's bright gaze.

In this high desert oasis, where the Nevada sun shines bright,
A new year dawns, with promise, hope, and endless light.
March 1st's arrival brings renewal, rebirth, and might,
To this city built on dreams, where hearts take flight.

As morning's beauty slowly unfurls, like a rose in bloom,
Reno's vibrant spirit stirs, with a gentle, loving tune.
In this moment, all is calm, as the world awakens slow,
And the desert's secrets whisper, of a day yet to be sown.
```

### Example 2: Morning in Wheeling

**Input:** 10:01 AM, Sat Mar 1, Wheeling WV

**Output:**
```
"River City Rhapsody"

On March's first morning, in Wheeling's gentle light,
At 10:01, the Ohio River's waters shine so bright.
The city stirs, with a quiet reverence, as dawn's warm rays
Awaken the hills and valleys, in a peaceful, lazy way.

The Point Park Bridge stretches, like a silver thread,
Connecting West Virginia to Ohio, where the river is fed.
The National Road, a historic path, once led pioneers west,
Now guides tourists and locals, through Wheeling's rich history and rest.

In this steel city town, where industry once thrived,
A new era unfolds, with heritage preserved and alive.
The Chesapeake & Ohio Railroad Station stands as a testament,
To the transcontinental dreams, that shaped America's progress and quest.

At 10:01 on March 1st, the morning air is crisp and clean,
As Wheeling's riverfront awakens, to a fresh new scene.
The scent of coal smoke wafts, like memories of old,
As the city rises, with stories yet untold.

In this charming Ohio River town, where history meets the present day,
A sense of community thrives, in a warm and welcoming way.
Wheeling's spirit is resilient, forged from steel and coal,
And on March 1st's morning dew, its beauty starts to unfold.
```

### Example 3: Afternoon in Reno

**Input:** 3:22 PM, Sat Mar 1, Reno NV

**Output:**
```
"In Reno's desert heart, where sunbeams play
At twenty-two past three, on March's first day
The world awakens, with a hint of spring's sway
As Nevada's high desert stretches out to gaze.

The Truckee River whispers secrets to the trees,
As willows and cottonwoods dance in gentle breeze
The mountains stand watch, a granite sentinel strong
Protecting the city's vibrant soul, where hearts belong

In this moment, time stands still, yet moves so fast
The world outside these streets is rushing past
But here, amidst the casinos' neon glow
A different rhythm beats, as the people go.

Their faces, etched with lines of love and strife
Reflect the tales of lives lived hard, with hearts full of life
The smell of fresh-cut grass wafts through the air
As winter's chill begins to fade, and spring's promise is shared

In Reno, on this first day of March's new start
Hope stirs, like a river flowing from the heart
A city born of dreams, where outcasts came to thrive
Now a tapestry rich with stories, woven alive."
```

## Models

The project works with the following Ollama models:
- llama3.1:8b (recommended base model)
- You can also use any other LLM available in your Ollama installation
- After training, you can create a custom model following the Modelfile template in test_model/

HuggingFace model mapping for training:
- llama3.1:8b maps to TinyLlama/TinyLlama-1.1B-Chat-v1.0
- mistral maps to mistralai/Mistral-7B-v0.1
- llama2 maps to TinyLlama/TinyLlama-1.1B-Chat-v1.0

## Testing

Run the integration test to verify your setup:
```
python scripts/test_integration.py
```

This will:
- Check if Ollama is installed and running
- Process a small test dataset (5 poems)
- Create a sample Modelfile
- Test poem generation using an existing Ollama model

## Recent Fixes and Improvements

The following issues have been fixed in the web application:

1. **API URL Configuration**
   - Fixed incorrect Ollama API URL in `.env` file
   - Changed from `http://localhost:11434/api/generate` to `http://localhost:11434`
   - This prevents malformed URL requests to Ollama

2. **Rate Limiting Adjustment**
   - Increased rate limit from 10 to 60 requests per minute
   - This accommodates multiple API calls made during each user request

3. **JavaScript Variable Name Conflict**
   - Fixed a variable name conflict in the `displayPoem` function
   - Renamed parameter from `poemContent` to `poemContentData` to avoid conflict with DOM element
   - This resolves the TypeError: "Cannot read properties of undefined (reading 'remove')"

These fixes ensure the web application can properly connect to Ollama and display poems without JavaScript errors.

## Limitations and Future Improvements

Current limitations:
- Synthetic data is template-based and may lack diversity
- Limited mapping between Ollama and HuggingFace models
- Location handling uses only names without geocoding
- LoRA configuration might not be optimal for all model architectures

Potential improvements:
- Use real poem datasets or more sophisticated generation
- Improve location handling with proper geocoding
- Add evaluation metrics for poem quality
- Implement user feedback mechanism
- Expand model compatibility
- Add caching to reduce API calls to Ollama
- Implement progressive enhancement for browsers without JavaScript

## License

[MIT License](LICENSE)
