import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from app.database.models import async_main
from app.handlers.admin import admin
from app.handlers.user import user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        await async_main()
        load_dotenv()
        bot = Bot(token=os.getenv('TG_TOKEN'))
        dp = Dispatcher()
        dp.include_routers(user, admin)
        await dp.start_polling(bot)
    except Exception as ex:
        logger.exception("Ошибка при запуске бота: %s", ex)
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')