#!/usr/bin/env python3
"""
Poem generation script using Ollama models.
This allows users to generate poems based on time, date, and location inputs.

Usage:
    # Interactive mode:
    python generate_poem.py --interactive
    
    # Direct generation with specific parameters:
    python generate_poem.py --model llama3.1:8b --time "18:30" --date "2023-10-21" --location "Paris" --temperature 0.7
    
Note:
    - Make sure to activate the virtual environment first: source venv/bin/activate
    - Requires Ollama to be installed and running
"""

import argparse
import json
import datetime
import pytz
import subprocess
from astral import LocationInfo
from astral.sun import sun

def parse_args():
    parser = argparse.ArgumentParser(description="Generate poems based on time, date, and location")
    parser.add_argument("--model", type=str, default="poem-generator", help="Name of the fine-tuned Ollama model")
    parser.add_argument("--time", type=str, help="Time in HH:MM format", required=True)
    parser.add_argument("--date", type=str, help="Date in YYYY-MM-DD format", required=True)
    parser.add_argument("--location", type=str, help="Location name", required=True)
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for generation")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    return parser.parse_args()

def validate_inputs(time_str, date_str, location):
    """Validate the input time, date, and location"""
    try:
        # Validate time format
        datetime.datetime.strptime(time_str, "%H:%M")
        
        # Validate date format
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        
        # Location is just a string, so we won't validate it
        return True
    except ValueError as e:
        print(f"Error: {e}")
        print("Time should be in HH:MM format (e.g., 14:30)")
        print("Date should be in YYYY-MM-DD format (e.g., 2023-10-21)")
        return False

def get_context_info(time_str, date_str, location):
    """Get additional context information about the time and place"""
    try:
        # Parse time and date
        hour, minute = map(int, time_str.split(":"))
        year, month, day = map(int, date_str.split("-"))
        
        # Create datetime object
        dt = datetime.datetime(year, month, day, hour, minute)
        
        # Determine time of day
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        # Determine season (Northern Hemisphere)
        if 3 <= month <= 5:
            season = "spring"
        elif 6 <= month <= 8:
            season = "summer"
        elif 9 <= month <= 11:
            season = "autumn"
        else:
            season = "winter"
        
        # Try to get sun position information (might not work for all locations)
        sun_info = None
        try:
            # Create a basic location info (this is approximate)
            loc = LocationInfo(location, location, "UTC", 0, 0)  # Default coords
            sun_info = sun(loc.observer, dt)
        except Exception:
            # If we can't get sun info, that's fine
            pass
        
        context = {
            "time_of_day": time_of_day,
            "season": season,
            "datetime": dt.isoformat(),
            "sun_info": str(sun_info) if sun_info else "Unknown"
        }
        
        return context
    except Exception as e:
        print(f"Warning: Could not get context information: {e}")
        return {}

def generate_poem(model_name, time_str, date_str, location, temperature=0.7):
    """Generate a poem using the specified Ollama model"""
    # Get context information
    context_info = get_context_info(time_str, date_str, location)
    
    # Create prompt with context
    prompt = f"Write a poem for {time_str} on {date_str} in {location}."
    
    # Add context to the prompt for better results
    if context_info:
        prompt += f"\n\nContext: It is {context_info.get('time_of_day')} during {context_info.get('season')}."
    
    try:
        # Check if model exists
        result = subprocess.run(["ollama", "list"], check=True, capture_output=True, text=True)
        available_models = []
        
        for line in result.stdout.strip().split('\n')[1:]:  # Skip header line
            if line:
                parts = line.split()
                if parts:
                    available_models.append(parts[0])
        
        model_exists = model_name in available_models
        
        if not model_exists:
            print(f"Model '{model_name}' not found. Available models:")
            for model in available_models:
                print(f"- {model}")
            return None
        
        # Generate poem
        print(f"Generating poem with model: {model_name}")
        print(f"Prompt: {prompt}")
        print("Generating...")
        
        # Use ollama run to generate the poem
        cmd = ["ollama", "run", model_name, "--temperature", str(temperature), prompt]
        response = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        return response.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error generating poem: {e}")
        print(f"Error details: {e.stderr}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def interactive_mode():
    """Run in interactive mode, asking for inputs"""
    print("=== Poem Generator Interactive Mode ===")
    
    # Get available models
    try:
        result = subprocess.run(["ollama", "list"], check=True, capture_output=True, text=True)
        available_models = []
        
        for line in result.stdout.strip().split('\n')[1:]:  # Skip header line
            if line:
                parts = line.split()
                if parts:
                    available_models.append(parts[0])
        
        print("Available models:")
        for i, model in enumerate(available_models):
            print(f"{i+1}. {model}")
        
        model_idx = int(input(f"Select model (1-{len(available_models)}): ")) - 1
        if model_idx < 0 or model_idx >= len(available_models):
            print("Invalid selection. Using default model.")
            model_name = "poem-generator"
        else:
            model_name = available_models[model_idx]
    except Exception as e:
        print(f"Error listing models: {e}")
        model_name = input("Enter model name (default: poem-generator): ") or "poem-generator"
    
    # Get parameters
    while True:
        time_str = input("Enter time (HH:MM): ")
        date_str = input("Enter date (YYYY-MM-DD): ")
        location = input("Enter location: ")
        temperature_str = input("Enter temperature (0.0-1.0, default: 0.7): ") or "0.7"
        temperature = float(temperature_str)
        
        # Validate inputs
        if validate_inputs(time_str, date_str, location):
            # Generate poem
            poem = generate_poem(model_name, time_str, date_str, location, temperature)
            
            if poem:
                print("\n=== Your Poem ===\n")
                print(poem)
                print("\n==================\n")
            else:
                print("Failed to generate poem. Please try again.")
        
        # Ask if the user wants to generate another poem
        again = input("Generate another poem? (y/n): ").lower()
        if again != 'y':
            break

def main():
    args = parse_args()
    
    # Run in interactive mode if specified
    if args.interactive:
        interactive_mode()
        return
    
    # Validate inputs
    if not validate_inputs(args.time, args.date, args.location):
        return
    
    # Generate poem
    poem = generate_poem(args.model, args.time, args.date, args.location, args.temperature)
    
    if poem:
        print("\n=== Your Poem ===\n")
        print(poem)
        print("\n==================\n")
    else:
        print("Failed to generate poem.")

if __name__ == "__main__":
    main()
