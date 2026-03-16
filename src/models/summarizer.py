import torch
from pathlib import Path
from transformers import T5Tokenizer, T5ForConditionalGeneration
from src.models.dataset import load_inference_dataset


MODEL_PATH = 'models/t5_arxiv_summarizer'
device = 'mps' if torch.backends.mps.is_available() else 'cpu'
tokenizer = T5Tokenizer.from_pretrained(MODEL_PATH)
model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH)
model.to(device)


def generate_summary(jsonl_path):
    dataset = load_inference_dataset(jsonl_path)
    text = dataset[0]['input_text']
    inputs = tokenizer(text,return_tensors='pt',truncation=True,max_length=512).to(device)
    outputs = model.generate(**inputs,max_length=128)
    summary = tokenizer.decode(outputs[0],skip_special_tokens=True)
    return summary