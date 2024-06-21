import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from app.database.models import async_main
from app.handlers.admin import admin
from app.handlers.user import user

async def main():
    await async_main()
    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()
    dp.include_routers(user, admin)
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')