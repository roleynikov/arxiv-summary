import json
from pathlib import Path
import pandas as pd


def find_latest_checkpoint(model_dir: Path):
    checkpoints = sorted(model_dir.glob('checkpoint-*'),key=lambda p: int(p.name.split('-')[-1]))
    return checkpoints[-1] if checkpoints else None


def extract_metrics(state_path: Path):
    with state_path.open(encoding='utf-8') as f:
        state = json.load(f)
    best = None
    for entry in state.get('log_history', []):
        if 'eval_rouge1' in entry:
            best = {
                'eval_loss': entry.get('eval_loss'),
                'rouge1': entry.get('eval_rouge1'),
                'rouge2': entry.get('eval_rouge2'),
                'rougeL': entry.get('eval_rougeL'),
                'epoch': entry.get('epoch')
            }
    return best


def main():
    rows = []
    models_dir = Path('models')
    for model_dir in models_dir.iterdir():
        if not model_dir.is_dir():
            continue
        ckpt = find_latest_checkpoint(model_dir)
        if ckpt is None:
            print(f'{model_dir.name} — checkpoint не найден')
            continue
        state_path = ckpt / 'trainer_state.json'
        if not state_path.exists():
            print(f'{model_dir.name} — trainer_state.json отсутствует')
            continue
        metrics = extract_metrics(state_path)
        if metrics is None:
            print(f'{model_dir.name} — метрики не найдены')
            continue
        print(f'{model_dir.name} — метрики загружены')
        rows.append({
            'model': model_dir.name,
            **metrics
        })
    if not rows:
        print('Метрики не найдены')
        return
    df = pd.DataFrame(rows).sort_values('model')
    print('\n=== RESULTS ===\n')
    print(df.to_string(index=False))
    save_path = models_dir / 'metrics_comparison.csv'
    df.to_csv(save_path, index=False)
    print(f'\nМетрики сохранены в {save_path}')


if __name__ == '__main__':
    main()