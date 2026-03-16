import json
import os
import time
from pathlib import Path
from tqdm import tqdm
from openai import OpenAI

GROQ_MODEL = 'llama-3.1-8b-instant' 
API_KEYS = [
    os.getenv('GROQ_API_KEY_1', ''),
    os.getenv('GROQ_API_KEY_2', ''),
    os.getenv('GROQ_API_KEY_3', '')
]

INPUT_PATH = Path('data/processed/articles.jsonl')
OUTPUT_PATH = Path('data/processed/articles_with_summary.jsonl')
MAX_CHARS = 12000

def build_prompt(article):
    text = article['text'][:MAX_CHARS]
    return f'''
Summarize the following scientific article.

Focus on problem, method, and results.
Write a concise summary (150-200 words).

Title:
{article.get('title', '')}

Abstract:
{article.get('abstract', '')}

Article:
{text}
'''


def groq_summary(prompt):
    last_exception = None
    for key in API_KEYS:
        if not key:
            continue
        client = OpenAI(
            api_key=key,
            base_url='https://api.groq.com/openai/v1'
        )
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.3
            )
            summary = response.choices[0].message.content.strip()
            return summary
        except Exception as e:
            print(f'API key failed: {key[:4]}..., trying next key. Error: {e}')
            last_exception = e
            time.sleep(2)

    raise RuntimeError(f'All API keys failed. Last error: {last_exception}')

def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with INPUT_PATH.open(encoding='utf-8') as f:
        articles = [json.loads(line) for line in f]
    with OUTPUT_PATH.open('w', encoding='utf-8') as out:
        for article in tqdm(articles):
            try:
                summary = groq_summary(build_prompt(article))
            except Exception as e:
                print(f'Failed to generate summary for article {article['article_id']}: {e}')
                continue
            article['summary'] = summary
            out.write(json.dumps(article, ensure_ascii=False) + '\n')
            out.flush()
            time.sleep(1)  
if __name__ == '__main__':
    main()