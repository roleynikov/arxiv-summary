import logging
from pathlib import Path
import requests
import time
logging.basicConfig(level=logging.INFO,format='%(asctime)s-%(levelname)s-%(message)s')
import os

GROBID_URL = os.getenv("GROBID_URL", "http://localhost:8070")

def process_pdf(pdf_path):
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    with pdf_path.open('rb') as f:
        response = requests.post(f"{GROBID_URL}/api/processFulltextDocument",files={'input': f},timeout=150)
    response.raise_for_status()
    time.sleep(0.5)
    return response.text

def parse_pdf(pdf_dir = Path('data/raw/pdfs'), output_dir = Path('data/raw/tei')):
    
    logging.info(f'Начинаем парсинг PDF')
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_files = list(pdf_dir.glob('*.pdf'))
    pdf_files = pdf_files[:500]
    for idx, pdf_path in enumerate(pdf_files, start=1):
        tei_path = output_dir / f'{pdf_path.stem}.tei.xml'
        if tei_path.exists():
            continue
        try:
            tei_xml = process_pdf(pdf_path)
            tei_path.write_text(tei_xml, encoding='utf-8')
            logging.info(f'{idx} -  Сохранено {tei_path.name}')
        except Exception as e:
            logging.warning(f'Ошибка при парсинге PDF - {pdf_path.name}: {e}')
    
    for pdf_path in pdf_files:
        pdf_path.unlink()
    logging.info(f'Все файлы PDF удалены')


if __name__ == '__main__':
    parse_pdf()
