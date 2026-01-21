import argparse
from pathlib import Path
import torch
import numpy as np
import evaluate
from transformers import T5ForConditionalGeneration,T5Tokenizer,Seq2SeqTrainer,Seq2SeqTrainingArguments
from src.models.dataset import load_dataset


rouge = evaluate.load('rouge')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target',type=str,required=True,choices=['abstract', 'introduction', 'conclusion'],help='Which section to use as target')
    args = parser.parse_args()

    target = args.target
    print(f'Обучаем на целевой переменной - {target}')

    device = ('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f'Тренируем на : {device}')

    dataset = load_dataset(Path('data/processed/sections.jsonl'), target=target)
    dataset = dataset.train_test_split(test_size=0.1, seed=1805)

    tokenizer = T5Tokenizer.from_pretrained('t5-small')
    model = T5ForConditionalGeneration.from_pretrained('t5-small')
    model.to(device)

    def compute_metrics(eval_pred):

        preds, labels = eval_pred
        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
        decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
        scores = rouge.compute(predictions=decoded_preds,references=decoded_labels)

        return {
            'rouge1': round(scores['rouge1'], 4),
            'rouge2': round(scores['rouge2'], 4),
            'rougeL': round(scores['rougeL'], 4)
        }


    def tokenize(batch):
        inputs = tokenizer(batch['input_text'],truncation=True,padding='max_length',max_length=512)
        targets = tokenizer(batch['target_text'],truncation=True,padding='max_length',max_length=128)
        inputs['labels'] = targets['input_ids']
        return inputs

    dataset = dataset.map(tokenize,batched=True,remove_columns=dataset['train'].column_names)
    out_dir = Path('models') / f't5_body2{target}'
    
    training_args = Seq2SeqTrainingArguments(
    output_dir=str(out_dir),
    eval_strategy='epoch',
    logging_strategy='epoch',
    save_strategy='epoch',
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=2,
    learning_rate=3e-4,
    num_train_epochs=1,
    weight_decay=0.01,
    save_total_limit=2,
    report_to='none',
    predict_with_generate=True,
    generation_max_length=128
    )

    trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset['train'],
    eval_dataset=dataset['test'],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
    )

    trainer.train()


if __name__ == '__main__':
    main()
