import json
import logging
import time
from pathlib import Path
import requests

logging.basicConfig(level=logging.INFO,format='%(asctime)s-%(levelname)s-%(message)s')


def download_pdfs(metadata=Path('data/raw') / 'metadata.json',output_dir=Path('data/raw') / 'pdfs'):
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.info('Начинаем скачивание PDF')
    with open(metadata, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    for idx, article in enumerate(articles , start=1):
        article_id = article['article_id']
        pdf_url = article['pdf_url']
        pdf_path = output_dir / f'{article_id}.pdf'
        if pdf_path.exists():
            logging.info(f'{idx} - PDF c {article_id} уже существует')
            continue
        try:
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            pdf_path.write_bytes(response.content)
            logging.info(f'{idx} - Скачан PDF - {article_id}')
            time.sleep(2)
        except Exception as e:
            logging.warning(f'{idx} - Ошибка при скачивании статьи - {article_id}: {e}')


if __name__ == '__main__':
    download_pdfs()
