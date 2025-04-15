import asyncio
from aiogram import Dispatcher, Bot
from config import TOKEN, CHANNEL_LINK
from app.admin import admin as admin_router 
from app.admin_ref import admin as admin_ref_router
from app.admin_withdraw import admin as admin_withdraw
from app.admin_bonus import admin as admin_bonus
from app.admin_statistics import admin as admin_stat
from app.admin_start import admin as admin_start
from app.admin_reminder import admin as admin_reminder
from app.user import user
from app.user_profile import user as user_profile
from app.database.models import async_main
from app.database.requests import create_config,check_subscriptions
#from app.middleware import SubscriptionMiddleware  # Импорт мидлвара

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # Регистрация мидлвара
    #dp.message.middleware(SubscriptionMiddleware(bot, CHANNEL_LINK))
    #dp.callback_query.middleware(SubscriptionMiddleware(bot, CHANNEL_LINK))

    # Регистрация роутеров
    dp.include_routers(admin_router, admin_ref_router, admin_withdraw, admin_bonus, admin_stat,admin_start ,admin_reminder, user, user_profile)
    dp.startup.register(on_startup)

    await dp.start_polling(bot)

async def on_startup(bot:Bot):
    await async_main()
    await create_config() 
    asyncio.create_task(check_subscriptions(bot))

    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
