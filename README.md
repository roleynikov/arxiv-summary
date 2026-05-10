
# Arxiv Summary Bot

Telegram-бот для автоматического скачивания, парсинга и саммаризации научных статей с arXiv с использованием моделей машинного обучения, основанных на трансформерной архитектуре.

---

# Возможности

* Получение статьи по `arXiv ID`
* Скачивание PDF
* Парсинг PDF через GROBID
* Построение датасета из научных статей
* Генерация summary
* Асинхронная обработка задач через RabbitMQ
* Хранение статусов задач в PostgreSQL
* Загрузка артефактов в S3
* Docker-based инфраструктура

---


# Стек

* Python
* aiogram
* PyTorch
* Transformers (HuggingFace)
* RabbitMQ
* PostgreSQL
* GROBID
* Docker Compose

---


# Запуск проекта

## 1. Создать `.env`

```env
TOKEN_TG=your_telegram_token

POSTGRES_DB=arxiv
POSTGRES_USER=app
POSTGRES_PASSWORD=app
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DB_URL=postgresql+psycopg2://app:app@postgres:5432/arxiv

S3_ENDPOINT=https://storage.yandexcloud.net
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
S3_BUCKET=your_bucket
S3_REGION=ru-central1

RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_QUEUE=arxiv_summary_tasks
RABBITMQ_USER=
RABBITMQ_PASSWORD=
GROBID_URL=http://grobid:8070
```

---

## 2. Запустить сервисы

```bash
docker compose up --build
```

---

# Сервисы

| Service     | Port  |
| ----------- | ----- |
| RabbitMQ    | 5672  |
| PostgreSQL  | 5432  |
| GROBID      | 8070  |

---

# Инициализация БД

После первого запуска:

```bash
docker exec -it worker python -m src.bot.init_db
```

---

# Использование бота

Отправьте боту arXiv ID:

```text
2401.12345
```

Бот:

1. скачает статью
2. распарсит PDF
3. создаст dataset
4. сгенерирует summary
5. отправит результат в Telegram

---

# Обучение модели

## Сбор метаданных статей

```bash
python -m src.data.fetch_arxiv
```

---

## Скачивание pdf-файлов

```bash
python -m src.data.download_pdfs
```

---

## Запуск GrobId

```bash
docker pull lfoppiano/grobid:0.7.3
docker run -d -p 8070:8070 lfoppiano/grobid:0.7.3
```

---


## Парсинг PDF

```bash
python -m src.data.parse_pdf
```

---



## Парсинг XML

```bash
python -m src.data.parse_xml
```

---

## Извлечение текста статьи

```bash
python -m src.data.dataset
```

---

## Генерация таргета при помощи Groq API

```bash
python -m src.models.generate_llm_summaries
```

---


## Обучение моделей

```bash
python -m src.models.train_t5
python -m src.models.train_bart_lora
python -m src.models.train_flan_t5_lora
```

---


# Метрики

Во время обучения используются:

* ROUGE-1
* ROUGE-2
* ROUGE-L
* BLEU
* BERTScore F1

---
