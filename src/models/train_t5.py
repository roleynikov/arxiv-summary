from pathlib import Path
import torch
import numpy as np
import evaluate
from transformers import (
    T5ForConditionalGeneration,
    T5Tokenizer,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments
)
from src.models.dataset import load_dataset


rouge = evaluate.load('rouge')


def main():
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f'Тренируем на: {device}')
    dataset = load_dataset(Path('data/processed/articles_with_summary.jsonl'))
    dataset = dataset.train_test_split(test_size=0.1, seed=1805)
    tokenizer = T5Tokenizer.from_pretrained('t5-small')
    model = T5ForConditionalGeneration.from_pretrained('t5-small')
    model.to(device)
    def compute_metrics(eval_pred):
        preds, labels = eval_pred
        if isinstance(preds, tuple):
            preds = preds[0]
        if preds.ndim == 3:
            preds = np.argmax(preds, axis=-1)
        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
        vocab_size = tokenizer.vocab_size
        preds = np.clip(preds, 0, vocab_size - 1)
        labels = np.clip(labels, 0, vocab_size - 1)
        decoded_preds = tokenizer.batch_decode(preds,skip_special_tokens=True)
        decoded_labels = tokenizer.batch_decode(labels,skip_special_tokens=True)
        scores = rouge.compute(predictions=decoded_preds,references=decoded_labels)

        return {'rouge1': round(scores['rouge1'], 4),'rouge2': round(scores['rouge2'], 4),'rougeL': round(scores['rougeL'], 4)}

    def tokenize(batch):
        inputs = tokenizer(batch['input_text'],truncation=True,padding='max_length',max_length=512)
        targets = tokenizer(batch['target_text'],truncation=True,padding='max_length',max_length=128)
        labels = targets['input_ids']
        labels = [[token if token != tokenizer.pad_token_id else -100 for token in label] for label in labels]
        inputs['labels'] = labels
        return inputs

    dataset = dataset.map(tokenize,batched=True,remove_columns=dataset['train'].column_names)
    out_dir = Path('models') / 't5_arxiv_summarizer'
    training_args = Seq2SeqTrainingArguments(
        output_dir=str(out_dir),
        eval_strategy='epoch',
        logging_strategy='epoch',
        save_strategy='epoch',
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=3e-4,
        num_train_epochs=15,
        weight_decay=0.01,
        save_total_limit=2,
        report_to='none',
        predict_with_generate=True,
        generation_max_length=128,
        generation_num_beams=4
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

    trainer.save_model(out_dir)
    tokenizer.save_pretrained(out_dir)
    print(f'Модель сохранена в {out_dir}')


if __name__ == '__main__':
    main()