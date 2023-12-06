import asyncio



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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot stopped!')
