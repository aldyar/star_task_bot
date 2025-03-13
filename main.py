import asyncio
from aiogram import Dispatcher, Bot
from config import TOKEN
from app.admin import admin as admin_router 
from app.admin_ref import admin as admin_ref_router
from app.admin_withdraw import admin as admin_withdraw
from app.user import user
from app.database.models import async_main
from app.database.requests import create_config


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_routers(admin_router,admin_ref_router,admin_withdraw, user)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)

async def on_startup(dispatcher):
    await async_main()
    await create_config() 

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass