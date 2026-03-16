import json
from pathlib import Path
from datasets import Dataset


def load_dataset(path: Path):
    records = []
    with path.open(encoding='utf-8') as f:
        for line in f:
            row = json.loads(line)
            records.append({
                'input_text': 'summarize: ' + row['text'],
                'target_text': row['summary']
            })
    return Dataset.from_list(records)


def load_inference_dataset(path: Path):
    records = []
    with path.open(encoding='utf-8') as f:
        for line in f:
            row = json.loads(line)
            records.append({
                'input_text': 'summarize: ' + row['text']
            })

    return Dataset.from_list(records)