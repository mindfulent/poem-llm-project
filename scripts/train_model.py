#!/usr/bin/env python3
"""
Training script for LoRA fine-tuning a small LLM on poem generation.
This script uses transformers and PEFT libraries to fine-tune a language model using the processed poem data.

Usage:
    # Make sure to activate the virtual environment first:
    source venv/bin/activate
    
    # Run with default parameters:
    python train_model.py
    
    # Run with custom parameters:
    python train_model.py --base_model llama3.1:8b --output_dir ./lora_model --batch_size 4 --epochs 3

Notes:
    - This script requires the processed data files in data/processed/
    - Run process_data.py first if you haven't generated the training data
    - Make sure Ollama is running with the base model available

After training:
    - Follow the instructions to create your Ollama model using the generated Modelfile
    - Use generate_poem.py to generate poems with your fine-tuned model
"""

import os
import json
import argparse
import torch
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType
)
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from datasets import Dataset
import requests
import ollama

class DataCollatorForTextDataset:
    """
    Custom data collator to handle text inputs for language modeling
    """
    def __init__(self, tokenizer, max_length=512):
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __call__(self, examples):
        texts = [example["text"] for example in examples]
        
        # Tokenize the texts
        batch = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        
        # Set the labels to the input_ids (for causal language modeling)
        batch["labels"] = batch["input_ids"].clone()
        
        return batch

def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tune a language model for poem generation")
    parser.add_argument("--base_model", type=str, default="llama3.1:8b", help="Base model to fine-tune")
    parser.add_argument("--output_dir", type=str, default="./lora_model", help="Directory to save the LoRA model")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size for training")
    parser.add_argument("--gradient_accumulation_steps", type=int, default=4, help="Gradient accumulation steps")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--learning_rate", type=float, default=2e-4, help="Learning rate")
    parser.add_argument("--lora_r", type=int, default=8, help="LoRA attention dimension")
    parser.add_argument("--lora_alpha", type=int, default=16, help="LoRA alpha parameter")
    parser.add_argument("--lora_dropout", type=float, default=0.1, help="LoRA dropout rate")
    
    return parser.parse_args()

def prepare_dataset(tokenizer=None):
    """
    Load and prepare the dataset for training
    """
    # Load processed data
    PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed")
    
    with open(os.path.join(PROCESSED_DATA_DIR, "train.json"), "r") as f:
        train_data = json.load(f)
    
    with open(os.path.join(PROCESSED_DATA_DIR, "val.json"), "r") as f:
        val_data = json.load(f)
    
    # Prepare datasets
    def format_prompt(example):
        """Format prompt for instruction tuning"""
        prompt = f"""### Instruction: 
{example['prompt']}

### Response:
{example['completion']}"""
        return {"text": prompt}
    
    train_formatted = [format_prompt(item) for item in train_data]
    val_formatted = [format_prompt(item) for item in val_data]
    
    train_dataset = Dataset.from_list(train_formatted)
    val_dataset = Dataset.from_list(val_formatted)
    
    return train_dataset, val_dataset

def prepare_ollama_model(base_model_name):
    """
    Prepare the Ollama model for fine-tuning
    """
    print(f"Preparing base model: {base_model_name}")
    
    # Check if model exists in Ollama
    try:
        # The response format is now a list of Model objects
        models_response = ollama.list()
        
        # Extract model names from the response
        model_names = []
        if hasattr(models_response, 'models'):
            # New API format
            for model in models_response.models:
                if hasattr(model, 'model'):
                    model_name = model.model.split(':')[0]
                    model_names.append(model_name)
        
        base_model_short_name = base_model_name.split(':')[0]
        
        if base_model_short_name not in model_names:
            print(f"Pulling {base_model_name} from Ollama repositories...")
            ollama.pull(base_model_name)
            
        print(f"Using model: {base_model_name}")
    except Exception as e:
        print(f"Error with Ollama: {e}")
        print("Please make sure Ollama is running and accessible.")
        return None, None
    
    # Convert the Ollama model name to a HuggingFace model name
    # Note: Using open-source models that don't require authentication
    hf_model_mapping = {
        "llama3.1:8b": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # Open source alternative
        "mistral": "mistralai/Mistral-7B-v0.1",
        "llama2": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # Open source alternative
    }
    
    if base_model_name in hf_model_mapping:
        hf_model_name = hf_model_mapping[base_model_name]
    else:
        # Fallback to a default open model
        hf_model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        print(f"No mapping found for {base_model_name}, using {hf_model_name} instead.")
    
    print(f"Using HuggingFace model: {hf_model_name}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(hf_model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Load base model without quantization 
    print("Loading model without quantization...")
    model = AutoModelForCausalLM.from_pretrained(
        hf_model_name,
        torch_dtype=torch.float32,  # Use float32 for better MPS compatibility
        device_map="auto",
    )
    
    return model, tokenizer

def train(args):
    """
    Train the model using LoRA
    """
    # Prepare model
    model, tokenizer = prepare_ollama_model(args.base_model)
    
    if model is None or tokenizer is None:
        print("Failed to prepare model and tokenizer. Exiting.")
        return
    
    # Prepare dataset
    train_dataset, val_dataset = prepare_dataset(tokenizer)
    
    # Configure LoRA
    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ]
    )
    
    # Create LoRA model
    model = get_peft_model(model, lora_config)
    
    # Print trainable parameters
    model.print_trainable_parameters()
    
    # Set up training arguments
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        num_train_epochs=args.epochs,
        weight_decay=0.01,
        push_to_hub=False,
        save_strategy="epoch",
        evaluation_strategy="epoch",
        load_best_model_at_end=True,
        fp16=False,  # Disable fp16 for MPS compatibility
        logging_steps=100,
        report_to="none",
        remove_unused_columns=False,  # Important for dataset column mismatch
    )
    
    # Create data collator
    data_collator = DataCollatorForTextDataset(tokenizer)
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
    )
    
    # Train model
    print("Starting training...")
    trainer.train()
    
    # Save model
    print(f"Saving LoRA model to {args.output_dir}")
    model.save_pretrained(args.output_dir)
    
    # Create Ollama modelfile
    modelfile_content = f"""
FROM {args.base_model}

# Poem Generator LoRA
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40

# System prompt
SYSTEM "You are a specialized AI trained to write beautiful poems based on time, date, and location inputs. Your poems should reflect the atmosphere, cultural context, and natural elements that would be present at the given time and place."
"""
    
    model_name = "poem-generator"
    
    # Write Modelfile
    with open(os.path.join(args.output_dir, "Modelfile"), "w") as f:
        f.write(modelfile_content)
    
    # Instructions for creating Ollama model
    print("\nTraining complete!")
    print("\nTo create your Ollama model, run:")
    print(f"cd {args.output_dir}")
    print(f"ollama create {model_name} -f Modelfile")
    print(f"\nThen you can use it with: ollama run {model_name}")

def main():
    args = parse_args()
    
    # Create output dir if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Train model
    train(args)

if __name__ == "__main__":
    main()
