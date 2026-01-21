from bs4 import BeautifulSoup
from pathlib import Path
import re

def normalize(text):
    return re.sub(r'\s+', ' ', text.strip())
 
def is_intro(title):
    title = title.lower()
    return any(k in title for k in {'introduction', 'background', 'motivation'})

def is_conclusion(title):
    title = title.lower()
    return any(k in title for k in {'conclusion', 'conclusions', 'summary', 'concluding remarks'})


def extract_sections_from_tei(tei_path):
    parse = BeautifulSoup(tei_path.read_text(encoding='utf-8'),'xml')
    article = {
        'article_id': tei_path.stem,
        'title': '',
        'abstract': '',
        'introduction': '',
        'conclusion': '',
        'body': ''
    }
    title_tag = parse.find('titleStmt')  
    if title_tag:
        title = title_tag.find('title')
        if title:
            article['title'] = normalize(title.text)
    abstract = parse.find('abstract')
    if abstract:
        article['abstract'] = normalize(abstract.text)
    introtudction = []
    conclusion= []
    body = []
    for div in parse.find_all('div'):
        head = div.find('head')
        title = normalize(head.text) if head else ''
        text = normalize(div.text.replace(title, ''))
        if not text:
            continue
        if title and is_intro(title):
            introtudction.append(text)
        elif title and is_conclusion(title):
            conclusion.append(text)
        else:
            body.append(text)
    article['introduction'] = '\n'.join(introtudction)
    article['conclusion'] = '\n'.join(conclusion)
    article['body'] = '\n'.join(body)
    return article
