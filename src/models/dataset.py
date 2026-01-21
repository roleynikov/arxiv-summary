import json
from pathlib import Path
from datasets import Dataset


def build_examples(data, target):
    examples = []
    for item in data:
        body = item.get('body', '').strip()
        tgt = item.get(target, '').strip()
        if not body or not tgt:
            continue
        examples.append({'input_text': body,'target_text': tgt})
    return examples

def load_dataset(path,target):
    data = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    examples = build_examples(data, target)
    return Dataset.from_list(examples)
