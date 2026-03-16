import json
import pika

QUEUE_NAME = 'arxiv_summary_tasks'


def get_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    return connection, channel


def publish_task(task):
    connection, channel = get_channel()
    channel.basic_publish(exchange='',routing_key=QUEUE_NAME,body=json.dumps(task),properties=pika.BasicProperties(delivery_mode=2))
    connection.close()