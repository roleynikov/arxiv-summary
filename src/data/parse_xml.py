from bs4 import BeautifulSoup
import re


def normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', text.strip())


def extract_fulltext_from_tei(tei_path):
    soup = BeautifulSoup(tei_path.read_text(encoding='utf-8'), 'xml')

    article = {
        'article_id': tei_path.stem,
        'title': '',
        'abstract': '',
        'text': ''
    }

    title_tag = soup.find('titleStmt')
    if title_tag:
        title = title_tag.find('title')
        if title:
            article['title'] = normalize(title.text)

    abstract = soup.find('abstract')
    if abstract:
        article['abstract'] = normalize(abstract.text)

    body = soup.find('body')
    paragraphs = []

    if body:
        for p in body.find_all('p'):
            text = normalize(p.text)
            if text:
                paragraphs.append(text)

    article['text'] = '\n'.join(paragraphs)

    return article