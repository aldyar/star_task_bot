from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from app.states import Chat, Image
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
#from app.generators import gpt_text, gpt_image
from app.database.requests import set_user, get_config, get_bonus_update, update_bonus, check_tasks
from aiogram.enums import ChatAction
from aiogram import Bot
import random
from datetime import datetime, timedelta

user = Router()


@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    emoji, captcha = random.choice(kb.captchas)  # Выбираем случайную капчу
    text = ("🤖 <b>Капча</b>\n\n"
        "1️⃣ Подпишись на <a href='https://t.me/testtt1143'>канал</a>\n\n"
        f"2️⃣ Нажми на {emoji} ниже, чтобы начать пользоваться ботом и получать звёзды, "
        "после прохождения начислим тебе 1⭐ на баланс бота:")
    await message.answer(text, reply_markup=captcha, parse_mode="HTML", disable_web_page_preview=True)


@user.message(F.text == '🎯Задания')
async def get_task(message: Message):
    tasks = await check_tasks(message.from_user.id)  # Получаем список доступных заданий

    if not tasks:
        await message.answer('Заданий пока нет. Задания появятся в ближайшее время.')
        return

    task = tasks[0]  # Берем первое доступное задание

    text = (
        f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"
        f"•<b> Подпишись на <a href='{task.link}'>{task.link}</a></b>\n"
        f"•<b> Награда: {task.reward}⭐</b>"
    )

    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)


@user.message(F.text == '💎Бонус')
async def bonus(message: Message):
    bonus = await get_config('bonus_amount')
    data = await get_bonus_update(message.from_user.id)
    now = datetime.now()  # Получаем текущее время в UTC
    if data is None or (now - data) >= timedelta(hours=24):
        text = (
            f'🌟 *Бонус в раз   мере {bonus}*⭐️ *начислен на ваш баланс в боте*.\n\n'

        '• *Повторно получить бонус можно через 24 часа.*'
        )
        await update_bonus(message.from_user.id, now,bonus)
    else: 
        remaining_time = timedelta(hours=24) - (now - data)
        hours, seconds = divmod(remaining_time.total_seconds(), 3600)
        minutes, _ = divmod(seconds, 60)
        
        text = (
            '❌ *Вы уже получали бонус недавно!*\n'
            f'💡 *Следующий бонус будет доступен через {int(hours)}ч {int(minutes)}м.*'
        )
    await message.answer(text,parse_mode='Markdown')

@user.callback_query(F.data == 'accsess')
async def success_callback(callback: CallbackQuery):
    await callback.answer("✅ Верно! Доступ разрешен.")
    await callback.message.delete()
    user = await callback.bot.get_chat(callback.from_user.id)
    username = user.username 
    await set_user(callback.from_user.id, username)

    text =   (
        "👋 *Добро пожаловать!*\n"
        "В нашем боте можно бесплатно зарабатывать звёзды, мы вывели уже более *250 тысяч звёзд*, посмотри –\n"
        "[🔗 https://t.me/testtt1143](https://t.me/testtt1143)\n\n"
        "🎁 *За регистрацию в боте, дарим тебе первую* `1⭐`, *получай больше звёзд этими способами:*\n"
        "• 🎯 *Выполняй задания*\n"
        "• 💎 *Забирай ежедневный бонус*\n"
        "• 👥 *Приглашай друзей по ссылке и получай по* `1.25⭐` *за каждого, просто отправь её другу:*\n"
        "[🔗 t.me/starfall_tg_bot?start=NjcxMjEwNTk1NQ](https://t.me/starfall_tg_bot?start=NjcxMjEwNTk1NQ)\n\n"
        "*Как только заработаешь минимум* `15⭐`, *выводи их в разделе* «💰 *Вывести звёзды*», *мы отправим тебе подарок за выбранное количество звёзд, удачи!*\n\n"
        "💬 *Наш чат:* [@fschatf](https://t.me/testtt1143)\n\n")
    await callback.message.answer(text,parse_mode="Markdown", reply_markup=kb.main, disable_web_page_preview=True)
    await callback.message.answer(' *🎯Выполняй лёгкие задания и лутай халявные звёзды:*',parse_mode="Markdown", reply_markup=kb.task_inline)


@user.message(F.text == '⭐️Заработать звёзды')
async def ref_system(message: Message):
    user_id = message.from_user.id
    referral_link = f"https://t.me/FreeStard_bot?start={user_id}"
    text = (
    "*Приглашай пользователей в бота и получай по 2*⭐, *как только они пройдут капчу!*\n\n"
    "*Ваша ссылка:*\n"
    f"[{referral_link}]({referral_link})\n\n"
    "❓ *Как использовать свою реферальную ссылку?*\n"
    "\n"
    "• *Отправь её друзьям в личные сообщения* 👥\n"
    "• *Поделись ссылкой в своём Telegram-канале* 📢\n"
    "• *Оставь её в комментариях или чатах* 💬\n"
    "• *Распространяй ссылку в соцсетях: TikTok, Instagram, WhatsApp и других* 🌐\n"
    "\n\n"
    "🗣 *Вы пригласили:* 0"
)



    await message.answer(text, disable_web_page_preview=True, parse_mode='Markdown')



@user.callback_query(F.data == 'void')
async def fail_callback(callback: CallbackQuery):
    await callback.answer("❌ Неверно!")
    await callback.message.delete()




@user.message(F.text == 'test')
async def get_username(message: Message,bot: Bot):
    user = await message.bot.get_chat(message.from_user.id)
    username = user.username if user.username else "У вас нет username"
    await message.answer(f"Ваш username: @{username}")
