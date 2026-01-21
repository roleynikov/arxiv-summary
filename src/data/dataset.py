import json
from pathlib import Path
from src.data.parse_xml import extract_sections_from_tei



def dataset():
    output_dir = Path('data/processed/sections.jsonl')
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    src_dir=Path('data/raw/tei')
    saved = 0
    with output_dir.open('w', encoding='utf-8') as f:
        for xml in src_dir.glob('*.tei.xml'):
            article = extract_sections_from_tei(xml)
            if not article['body']:
                continue
            f.write(json.dumps(article, ensure_ascii=False) + '\n')
            saved += 1
    print(f'{saved} статей сохранено в {output_dir}')

if __name__ == '__main__':
    dataset()
