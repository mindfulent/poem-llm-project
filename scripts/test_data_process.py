
import os
import json
import random
from datetime import datetime, timedelta

# Create paths
RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed")

# Ensure directories exist
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# Generate a few test poems
poems = []
for i in range(5):
    poem = {
        "title": f"Test Poem {i+1}",
        "time": f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}",
        "date": f"2023-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
        "location": random.choice(["Paris", "New York", "Tokyo", "London", "Sydney"]),
        "content": f"This is test poem number {i+1}\nWith multiple lines\nFor testing purposes\nWith love from the test suite.",
        "metadata": {
            "time_of_day": random.choice(["morning", "day", "evening", "night"]),
            "season": random.choice(["spring", "summer", "autumn", "winter"]),
            "themes": ["test", "poem"]
        }
    }
    poems.append(poem)

# Save raw data
with open(os.path.join(RAW_DATA_DIR, "test_poems.json"), "w") as f:
    json.dump(poems, f, indent=2)

# Format for training
formatted_data = []
for poem in poems:
    prompt = f"Write a poem for {poem['time']} on {poem['date']} in {poem['location']}."
    formatted_data.append({
        "prompt": prompt,
        "completion": poem['content'],
        "metadata": poem['metadata']
    })

# Save processed data
with open(os.path.join(PROCESSED_DATA_DIR, "training_data.json"), "w") as f:
    json.dump(formatted_data, f, indent=2)

# Create train/val split (simple for test)
train_data = formatted_data[:3]
val_data = formatted_data[3:]

# Save train/val splits
with open(os.path.join(PROCESSED_DATA_DIR, "train.json"), "w") as f:
    json.dump(train_data, f, indent=2)
    
with open(os.path.join(PROCESSED_DATA_DIR, "val.json"), "w") as f:
    json.dump(val_data, f, indent=2)

print(f"Created {len(poems)} test poems")
print(f"Training set: {len(train_data)}")
print(f"Validation set: {len(val_data)}")
print("Test data processing completed successfully!")
