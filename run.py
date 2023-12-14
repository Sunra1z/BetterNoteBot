import asyncio
import logging

import telebot
from aiogram import Bot, Dispatcher

from handlers import router
from database.models import async_main
from config import TOKEN
bot = Bot(token=TOKEN)
async def main():
    await async_main()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filename='bot.log', format='%(asctime)s %(levelname)s %(name)s %(message)s') # Logging system saves into file
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot stopped!')


