#!/usr/bin/env python3
"""
Data processor for poem dataset with time, date, and location metadata.
This script will generate a synthetic poem dataset and format it for LoRA fine-tuning.

Usage:
    # Make sure to activate the virtual environment first:
    source venv/bin/activate
    
    # Then run the script:
    python process_data.py
    
Output:
    - Creates synthetic_poems.json in data/raw/
    - Creates training_data.json, train.json, and val.json in data/processed/
"""

import os
import json
import random
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm
import requests
import pytz
from astral import LocationInfo
from astral.sun import sun

# Create paths
RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed")

# Ensure directories exist
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

def download_poem_dataset():
    """
    Download poem dataset or create a synthetic one if not available.
    For demonstration, we'll create a synthetic dataset.
    
    In a production environment, you might want to use a real dataset like:
    - PoetryDB API
    - Project Gutenberg poetry collections
    - Poetry Foundation dataset
    """
    print("Creating synthetic poem dataset...")
    
    # List of poem themes based on time of day
    morning_themes = ["dawn", "sunrise", "awakening", "dew", "beginnings", "fresh", "morning"]
    day_themes = ["sun", "light", "warmth", "activity", "journey", "work", "brightness"]
    evening_themes = ["sunset", "dusk", "reflection", "calm", "winding down", "golden hour", "shadows"]
    night_themes = ["stars", "moon", "dreams", "silence", "mystery", "darkness", "sleep"]
    
    # List of seasons and their themes
    seasonal_themes = {
        "spring": ["rebirth", "growth", "flowers", "rain", "green", "hope", "youth"],
        "summer": ["heat", "abundance", "vacation", "play", "ocean", "harvest", "freedom"],
        "autumn": ["falling leaves", "change", "harvest", "nostalgia", "golden", "transition", "melancholy"],
        "winter": ["snow", "silence", "introspection", "rest", "cold", "endurance", "darkness"]
    }
    
    # List of sample locations
    locations = [
        "New York", "Paris", "Tokyo", "London", "Sydney", "Cairo", "Rio de Janeiro", 
        "Mumbai", "Moscow", "Cape Town", "Beijing", "Rome", "Vancouver", "Mexico City",
        "mountain", "forest", "beach", "desert", "countryside", "village", "city center",
        "riverside", "lakeside", "island", "garden", "valley", "hillside", "ocean"
    ]
    
    # Generate synthetic poem data
    poems = []
    start_date = datetime(2020, 1, 1)
    
    for i in tqdm(range(500)):  # Generate 500 synthetic poems
        # Random date within 3 years
        random_days = random.randint(0, 365 * 3)
        poem_date = start_date + timedelta(days=random_days)
        date_str = poem_date.strftime("%Y-%m-%d")
        
        # Random time
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        time_str = f"{hour:02d}:{minute:02d}"
        
        # Determine time of day and appropriate themes
        if 5 <= hour < 12:
            time_of_day = "morning"
            themes = morning_themes
        elif 12 <= hour < 17:
            time_of_day = "day"
            themes = day_themes
        elif 17 <= hour < 21:
            time_of_day = "evening"
            themes = evening_themes
        else:
            time_of_day = "night"
            themes = night_themes
        
        # Determine season
        month = poem_date.month
        if 3 <= month <= 5:
            season = "spring"
        elif 6 <= month <= 8:
            season = "summer"
        elif 9 <= month <= 11:
            season = "autumn"
        else:
            season = "winter"
            
        # Random location
        location = random.choice(locations)
        
        # Generate a short poem title
        theme_words = themes + seasonal_themes[season]
        title = f"The {random.choice(theme_words).capitalize()} {random.choice(['of', 'in', 'at', 'during', 'beyond'])} {random.choice(theme_words).capitalize()}"
        
        # Generate a placeholder for poem content
        # In a real scenario, this would be actual poem content
        # For now, we'll use placeholder text that mentions the appropriate themes
        theme_word1 = random.choice(themes)
        theme_word2 = random.choice(seasonal_themes[season])
        
        content = f"""In the {time_of_day}'s {theme_word1} glow,
Where {location}'s {theme_word2} sings,
The {season}'s touch reminds us so,
Of what each moment brings.

Time passes like {random.choice(themes)},
On this {date_str} we find,
That {random.choice(seasonal_themes[season])} always frees,
Our hearts and stirs our mind."""

        poems.append({
            "title": title,
            "time": time_str,
            "date": date_str,
            "location": location,
            "content": content,
            "metadata": {
                "time_of_day": time_of_day,
                "season": season,
                "themes": [random.choice(themes), random.choice(seasonal_themes[season])]
            }
        })
    
    # Save raw data
    with open(os.path.join(RAW_DATA_DIR, "synthetic_poems.json"), "w") as f:
        json.dump(poems, f, indent=2)
    
    return poems

def format_for_training(poems):
    """
    Format the poem data for LoRA training.
    This creates a prompt-completion format suitable for instruction fine-tuning.
    """
    formatted_data = []
    
    for poem in tqdm(poems):
        # Create a prompt based on time, date, and location
        prompt = f"Write a poem for {poem['time']} on {poem['date']} in {poem['location']}."
        
        # Add some variations for prompt diversity
        variant = random.randint(1, 4)
        if variant == 1:
            prompt = f"Compose a poem inspired by {poem['location']} at {poem['time']} on {poem['date']}."
        elif variant == 2:
            prompt = f"Create a verse about {poem['location']} at {poem['time']} on the date {poem['date']}."
        elif variant == 3:
            prompt = f"Write poetry that captures the essence of {poem['location']} at {poem['time']} on {poem['date']}."
        
        # Format for training
        formatted_data.append({
            "prompt": prompt,
            "completion": poem['content'],
            "metadata": {
                "title": poem['title'],
                "time": poem['time'],
                "date": poem['date'],
                "location": poem['location'],
                "time_of_day": poem['metadata']['time_of_day'],
                "season": poem['metadata']['season']
            }
        })
    
    # Save processed data
    with open(os.path.join(PROCESSED_DATA_DIR, "training_data.json"), "w") as f:
        json.dump(formatted_data, f, indent=2)
    
    # Create train/val split
    random.shuffle(formatted_data)
    split_idx = int(len(formatted_data) * 0.9)  # 90% train, 10% validation
    
    train_data = formatted_data[:split_idx]
    val_data = formatted_data[split_idx:]
    
    # Save train/val splits
    with open(os.path.join(PROCESSED_DATA_DIR, "train.json"), "w") as f:
        json.dump(train_data, f, indent=2)
        
    with open(os.path.join(PROCESSED_DATA_DIR, "val.json"), "w") as f:
        json.dump(val_data, f, indent=2)
    
    print(f"Processed {len(formatted_data)} poems.")
    print(f"Training set: {len(train_data)}")
    print(f"Validation set: {len(val_data)}")
    
    return formatted_data

def main():
    print("Processing poem data...")
    
    # Download or create poem dataset
    poems = download_poem_dataset()
    
    # Format data for training
    formatted_data = format_for_training(poems)
    
    print("Data processing complete!")

if __name__ == "__main__":
    main()
