import asyncio
from aiogram import Dispatcher, Bot
from config import TOKEN, CHANNEL_LINK
from handlers.admin import admin as admin_router 
from handlers.admin_ref import admin as admin_ref_router
from handlers.admin_withdraw import admin as admin_withdraw
from handlers.admin_bonus import admin as admin_bonus
from handlers.admin_statistics import admin as admin_stat
from handlers.admin_start import admin as admin_start
from handlers.admin_reminder import admin as admin_reminder
from handlers.admin_event import admin as admin_event
from handlers.admin_link_stat import admin as admin_link_stat
from handlers.admin_mini_adds import admin as admin_mini_adds
from handlers.admin_promocode import admin as admin_promocode
from handlers.user import user
from handlers.user_profile import user as user_profile
from handlers.user_top import user as user_top
from handlers.user_subgram import user as user_subgram
from handlers.user_check import user as user_check
from database.models import async_main
from database.requests import create_config,check_subscriptions
#from handlers.middleware import SubscriptionMiddleware  # Импорт мидлвара
from database.asyncio_task import event_watcher


from app.api import app as fastapi_app
from uvicorn import Config, Server


async def start_fastapi():
    config = Config(app=fastapi_app, host="0.0.0.0", port=5000, log_level="info")
    server = Server(config)
    await server.serve()


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # Регистрация мидлвара
    #dp.message.middleware(SubscriptionMiddleware(bot, CHANNEL_LINK))
    #dp.callback_query.middleware(SubscriptionMiddleware(bot, CHANNEL_LINK))

    # Регистрация роутеров
    dp.include_routers(admin_router, admin_ref_router, admin_withdraw, admin_bonus, admin_stat,admin_start,
                       admin_reminder,admin_event,admin_link_stat,admin_mini_adds,admin_promocode,
                       user, user_profile, user_top,user_subgram,user_check)
    dp.startup.register(on_startup)

    # await asyncio.gather(
    #     dp.start_polling(bot),
    #     start_fastapi()
    # )
    await dp.start_polling(bot)
async def on_startup(bot:Bot):
    print('✅BOT STARTED')
    await async_main()
    await create_config() 
    asyncio.create_task(check_subscriptions(bot=bot))
    asyncio.create_task(event_watcher(bot))

    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
