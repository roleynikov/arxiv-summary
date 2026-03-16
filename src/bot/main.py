import asyncio
import re
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from src.bot.queue import publish_task

TOKEN_TG = os.environ.get('TOKEN_TG')
bot = Bot(token=TOKEN_TG)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        'Отправь ссылку на arXiv статью.\n\n'
        'Например:\n'
        'https://arxiv.org/abs/2401.12345'
    )


@dp.message()
async def handle_article(message: Message):
    arxiv_id = re.search(r'\d{4}\.\d{4,5}', message.text)
    arxiv_id = arxiv_id.group(0) if arxiv_id else None
    if not arxiv_id:
        await message.answer(
            'Не удалось определить arXiv id.\n'
            'Отправь ссылку вида:\n'
            'https://arxiv.org/abs/2401.12345'
        )
        return
    publish_task({'chat_id': message.chat.id,'arxiv_id': arxiv_id})
    await message.answer(
        f'Статья {arxiv_id} отправлена на обработку.\n'
        'Подождите ~30-60 секунд.'
    )

async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())