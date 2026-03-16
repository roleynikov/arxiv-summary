import json
from pathlib import Path
from src.data.parse_xml import extract_fulltext_from_tei


def dataset(src_dir = Path('data/raw/tei'), output_path = Path('data/processed/articles.jsonl')):
    output_path.parent.mkdir(parents=True, exist_ok=True)    
    saved = 0
    with output_path.open('w', encoding='utf-8') as f:
        for xml in src_dir.glob('*.tei.xml'):
            article = extract_fulltext_from_tei(xml)
            if not article['text']:
                continue
            f.write(json.dumps(article, ensure_ascii=False) + '\n')
            saved += 1
    print(f'{saved} статей сохранено в {output_path}')

if __name__ == '__main__':
    dataset()