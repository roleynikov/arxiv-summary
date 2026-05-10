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
from src.bot.s3_client import upload_dir, upload_file
from src.bot.db import create_job, update_job
from src.bot.db import init_db
import os

TOKEN_TG = os.getenv("TOKEN_TG")
QUEUE_NAME = 'arxiv_summary_tasks'
bot = Bot(token=TOKEN_TG)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def send_message(chat_id, text):
    await bot.send_message(chat_id, text)

def run_pipeline(arxiv_id, job_id):
    tmp_dir = Path('/tmp') / job_id
    tmp_dir.mkdir(parents=True)
    try:
        articles = fetch_single_arxiv(arxiv_id)
        metadata_path = save_metadata(articles, tmp_dir)
        upload_file(metadata_path, f"jobs/{job_id}/metadata.json")
        pdf_dir = tmp_dir / "pdfs"
        download_pdfs(metadata_path, pdf_dir)
        for pdf in pdf_dir.glob("*.pdf"):
            upload_file(pdf, f"jobs/{job_id}/pdfs/{pdf.name}")
        tei_dir = tmp_dir / "tei"
        parse_pdf(pdf_dir, tei_dir)
        for tei in tei_dir.glob("*.xml"):
            upload_file(tei, f"jobs/{job_id}/tei/{tei.name}")
        dataset_path = tmp_dir / "articles.jsonl"
        dataset(tei_dir, dataset_path)
        upload_file(dataset_path, f"jobs/{job_id}/articles.jsonl")
        summary = generate_summary(dataset_path)
        update_job(job_id,status="done")
        return summary
    except Exception as e:
        update_job(job_id, status="failed")
        raise e


def callback(ch, method, properties, body):
    data = json.loads(body)
    chat_id = data['chat_id']
    arxiv_id = data['arxiv_id']
    job_id = str(uuid.uuid4())
    create_job(job_id, chat_id, arxiv_id)
    try:
        summary = run_pipeline(arxiv_id,job_id)
        loop.run_until_complete(send_message(chat_id,f'Summary for {arxiv_id}\n\n{summary}'))
    except Exception as e:
        loop.run_until_complete(send_message(chat_id,f'Ошибка обработки статьи:\n{e}'))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_consume(queue=QUEUE_NAME,on_message_callback=callback)
    print('Worker запущен')
    channel.start_consuming()

if __name__ == '__main__':
    init_db()   
    main()