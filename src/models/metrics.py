import json
from pathlib import Path
import pandas as pd

def find_latest_checkpoint(model_dir):
    checkpoints = sorted(model_dir.glob('checkpoint-*'),key=lambda p: int(p.name.split('-')[-1]))
    return checkpoints[-1] if checkpoints else None


def extract_metrics(trainer_state_path):
    with trainer_state_path.open('r', encoding='utf-8') as f:
        state = json.load(f)
    for entry in reversed(state.get('log_history', [])):
        if 'eval_rouge1' in entry:
            return {
                'eval_loss': entry.get('eval_loss'),
                'rouge1': entry.get('eval_rouge1'),
                'rouge2': entry.get('eval_rouge2'),
                'rougeL': entry.get('eval_rougeL'),
                'epoch': entry.get('epoch')
            }
    return None


def main():
    rows = []
    models = Path('models')
    for model_dir in models.iterdir():
        if not model_dir.is_dir():
            continue
        ckpt_dir = find_latest_checkpoint(model_dir)
        state_path = ckpt_dir / 'trainer_state.json'
        metrics = extract_metrics(state_path)
        target = model_dir.name.replace('t5_body2', '')
        print(f'{model_dir.name} - метрики загружены')
        rows.append({'target': target,**metrics})
    df = pd.DataFrame(rows).sort_values('target')
    print(df.to_string(index=False))
    save_df = models/ 'metrics_comparison.csv'
    df.to_csv(save_df, index=False)
    print(f'Метрики сохранены в {save_df}')


if __name__ == '__main__':
    main()
