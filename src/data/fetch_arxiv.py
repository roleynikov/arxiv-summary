import time
import json
import logging
from pathlib import Path
import feedparser

CATEGORY = 'cs.CL'
AMOUNT = 100
BATCH_SIZE = 10


logging.basicConfig(level=logging.INFO,format='%(asctime)s-%(levelname)s-%(message)s')


def fetch_arxiv():
    articles = []
    start = 0
    logging.info('Начинаем парсинг статей')
    while len(articles) < AMOUNT:
        query = (
            f'search_query=cat:{CATEGORY}'
            f'&start={start}'
            f'&max_results={BATCH_SIZE}'
            '&sortBy=submittedDate'
            '&sortOrder=descending'
        )
        parser = feedparser.parse(f'http://export.arxiv.org/api/query?{query}')
        if not parser.entries:
            break
        for entry in parser.entries:
            pdf_link = next((link.href for link in entry.links if link.type == 'application/pdf'),None)
            if pdf_link is None:
                continue
            articles.append({
                'article_id': entry.id.split('/')[-1],
                'title': entry.title.strip().replace('\n', ' '),
                'abstract': entry.summary.strip().replace('\n', ' '),
                'pdf_url': pdf_link
            })
        start += BATCH_SIZE
        logging.info(f'Спарсили {len(articles)} статей')
        time.sleep(3)  
    return articles


def save_metadata(articles):
    output_dir = Path('data/raw')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'metadata.json'
    with open(output_path, 'w', encoding='utf-8') as output:
        json.dump(articles, output, ensure_ascii=False,indent=2)
    logging.info(f'Метаданные сохранены в  {output_path}')


if __name__ == '__main__':
    articles = fetch_arxiv()
    save_metadata(articles)
