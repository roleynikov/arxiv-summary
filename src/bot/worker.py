import json
import pika
import asyncio
import uuid
import shutil
import os
from pathlib import Path
from aiogram import Bot
from src.data.fetch_arxiv import fetch_single_arxiv, save_metadata
from src.models.summarizer import generate_summary
from src.data.download_pdfs import download_pdfs
from src.data.parse_pdf import parse_pdf
from src.data.dataset import dataset


QUEUE_NAME = 'arxiv_summary_tasks'
TOKEN_TG = os.environ.get('TOKEN_TG')
bot = Bot(token=TOKEN_TG)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def send_message(chat_id, text):
    await bot.send_message(chat_id, text)


def run_pipeline(arxiv_id):
    job_id = str(uuid.uuid4())
    job_dir = Path('data/jobs') / job_id
    job_dir.mkdir(parents=True)
    raw_dir = job_dir / 'raw'
    pdfs_dir = raw_dir / 'pdfs'
    tei_dir = raw_dir / 'tei'
    processed_dir = job_dir / 'processed'
    articles = fetch_single_arxiv(arxiv_id)
    metadata_path = save_metadata(articles, raw_dir) 
    download_pdfs(metadata_path, pdfs_dir)
    parse_pdf(pdfs_dir, tei_dir)
    dataset(tei_dir, processed_dir / 'articles.jsonl')
    summary = generate_summary(processed_dir / 'articles.jsonl')
    shutil.rmtree(job_dir)
    return summary


def callback(ch, method, properties, body):
    data = json.loads(body)
    chat_id = data['chat_id']
    arxiv_id = data['arxiv_id']
    try:
        summary = run_pipeline(arxiv_id)
        loop.run_until_complete(send_message(chat_id,f'Summary for {arxiv_id}\n\n{summary}'))
    except Exception as e:
        loop.run_until_complete(send_message(chat_id,f'Ошибка обработки статьи:\n{e}'))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_consume(queue=QUEUE_NAME,on_message_callback=callback)
    print('Worker запущен')
    channel.start_consuming()

if __name__ == '__main__':
    main()