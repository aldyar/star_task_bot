from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.database.requests import (set_user, get_config, get_bonus_update, update_bonus, check_tasks, get_user, 
                                   get_withdraw_limit, set_referrer_id, create_transaction, get_task,
                                   is_user_subscribed,completed_task,create_task_completions,check_subscriptions,
                                   check_user)
from app.keyboards import withdraw_inline, withdraw_keyboard
from aiogram.enums import ChatAction
from aiogram import Bot
import random
from datetime import datetime, timedelta
import text as txt
user = Router()
from config import ADMIN
from app.admin import start_admin
import uuid

@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if user:  # Если пользователь уже есть в базе данных
        await success_message(message)
        return
    

    if len(message.text.split()) > 1:
        referrer_id = int(message.text.split(maxsplit=1)[1])
        await state.update_data(referrer_id=referrer_id)
    emoji, captcha = random.choice(kb.captchas)  # Выбираем случайную капчу
    text = ("🤖 <b>Капча</b>\n\n"
        "1️⃣ Подпишись на <a href='https://t.me/FreeStard'>канал</a>\n\n"
        f"2️⃣ Нажми на {emoji} ниже, чтобы начать пользоваться ботом и получать звёзды, "
        "после прохождения начислим тебе 1⭐ на баланс бота:")
    await message.answer(text, reply_markup=captcha, parse_mode="HTML", disable_web_page_preview=True)


async def success_message(message: Message):
    start = await get_config('start_text')
    await message.answer(start,parse_mode="Markdown", reply_markup=kb.main, disable_web_page_preview=True)
    await message.answer(' *🎯Выполняй лёгкие задания и лутай халявные звёзды:*',parse_mode="Markdown", reply_markup=kb.task_inline)


@user.message(F.text == '🎯Задания')
async def get_task_hander(message: Message,state: FSMContext):
    task = await get_task(message.from_user.id)  # Получаем список доступных заданий

    if not task:
        await message.answer('Заданий пока нет. Задания появятся в ближайшее время.')
        return

    text = (
        f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"
        f"•<b> Подпишись на <a href='{task.link}'>{task.link}</a></b>\n"
        f"•<b> Награда: {task.reward}⭐</b>"
    )
    await state.update_data(task = task)


    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=kb.complete_inline)


@user.callback_query(F.data == 'complete_task')
async def complete_task_handler(callback:CallbackQuery,bot:Bot,state:FSMContext):
    data = await state.get_data()
    task_present = data.get("task")
    await state.clear()
    
    link = task_present.link
    is_subscribed  = await is_user_subscribed(bot,callback.from_user.id,link)
    if is_subscribed :
        copmpleted = await completed_task(task_present.id, callback.from_user.id, task_present.reward)
        if copmpleted:
            message_text = (f'🎯*Задание под номером  №*{task_present.id} *завершило работу*\n\n'
                            f'• *Ссылка на задание:* [{task_present.link}]({task_present.link})\n'
                            f'• *Колличество выполнений:*{task_present.completed_count}')
            for admin_id in ADMIN:
                await bot.send_message(admin_id, message_text,parse_mode='Markdown', disable_web_page_preview=True)
        await callback.answer('⭐Вознаграждения зачислено')
        await create_task_completions(callback.from_user.id,task_present.id)
        await callback.message.delete()
        task = await get_task(callback.from_user.id)  # Получаем список доступных заданий
        await state.update_data(task = task)

        if not task:
            await callback.message.answer('Заданий пока нет. Задания появятся в ближайшее время.')
            return



        text = (
            f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"
            f"•<b> Подпишись на <a href='{task.link}'>{task.link}</a></b>\n"
            f"•<b> Награда: {task.reward}⭐</b>"
        )

        await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=kb.complete_inline)
    else:
        await callback.answer("❌ Вы не подписаны на канал! Подпишитесь и попробуйте снова.", show_alert=True)

@user.message(F.text == '💎Бонус')
async def bonus(message: Message):
    bonus = await get_config('bonus_amount')
    data = await get_bonus_update(message.from_user.id)
    now = datetime.now()  # Получаем текущее время в UTC
    if data is None or (now - data) >= timedelta(hours=24):
        text = (
            f'🌟 *Бонус в размере {bonus}*⭐️ *начислен на ваш баланс в боте*.\n\n'

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
async def success_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    referrer_id = data.get("referrer_id")
    await callback.answer("✅ Верно! Доступ разрешен.")
    await callback.message.delete()
    user = await callback.bot.get_chat(callback.from_user.id)
    username = user.username 
    await set_user(callback.from_user.id, username, referrer_id)
    start = await get_config('start_text')
    await callback.message.answer(start,parse_mode="Markdown", reply_markup=kb.main, disable_web_page_preview=True)
    await callback.message.answer(' *🎯Выполняй лёгкие задания и лутай халявные звёзды:*',parse_mode="Markdown", reply_markup=kb.task_inline)


@user.callback_query(F.data == 'task')
async def task_handler(callback:CallbackQuery, state:FSMContext):
    task = await get_task(callback.from_user.id)  # Получаем список доступных заданий

    if not task:
        await callback.message.answer('Заданий пока нет. Задания появятся в ближайшее время.')
        return

    text = (
        f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"
        f"•<b> Подпишись на <a href='{task.link}'>{task.link}</a></b>\n"
        f"•<b> Награда: {task.reward}⭐</b>"
    )
    await state.update_data(task = task)


    await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=kb.complete_inline)
    await callback.answer()

@user.message(F.text == '⭐️Заработать звёзды')
async def ref_system(message: Message):
    user_id = message.from_user.id
    referral_link = f"https://t.me/FreeStard_bot?start={user_id}"
    change_text = await get_config('ref_text')
    user = await get_user(user_id)
    text = (
    f'{change_text}\n\n'
    "*Ваша ссылка:*\n"
    f"`{referral_link}`\n\n"
    "❓ *Как использовать свою реферальную ссылку?*\n"
    "\n"
    "• *Отправь её друзьям в личные сообщения* 👥\n"
    "• *Поделись ссылкой в своём Telegram-канале* 📢\n"
    "• *Оставь её в комментариях или чатах* 💬\n"
    "• *Распространяй ссылку в соцсетях: TikTok, Instagram, WhatsApp и других* 🌐\n"
    "\n\n"
    f"🗣 *Вы пригласили:* {user.referral_count}"
)



    await message.answer(text, disable_web_page_preview=True, parse_mode='Markdown')


@user.message(F.text == '🎁Вывести звёзды')
async def withdraw(message:Message):
    user = await get_user(message.from_user.id)
    keyboard = await withdraw_keyboard()
    text = (
        f"*Заработано: {user.balance}⭐️*\n\n"
        '*🔻 Выбери, подарок за сколько звёзд хочешь получить:*'
    )
    await message.answer(text, parse_mode='Markdown', reply_markup=keyboard)



@user.callback_query(lambda c: c.data and c.data.startswith("withdraw_"))
async def handle_withdraw_callback(callback: CallbackQuery, bot: Bot):
    value = int(callback.data.removeprefix("withdraw_")) 
    user = await get_user(callback.from_user.id)
    if user.balance >= value:  
        text = (
    f"*⏳ Заявка на вывод {value}⭐ создана!*\n\n"
    "*В течение 72 часов заявка будет рассмотрена администраторами и вам будет отправлен подарок,* "
    "*из которого вы получите звёзды.*\n\n"
    "*Следить за статусом своей заявки можно в нашем чате выводов в реальном времени:* [https://t.me/stoutput](https://t.me/stoutput)\n\n"
    "_Не меняйте @username, иначе мы не сможем отправить подарок, а заявка будет отклонена!_"
)
        message_text = (
        f"📢 Новая заявка на вывод!\n\n"
        f"👤 Пользователь: {user.username or 'Не указан'}\n"
        f"🆔 TG ID: {user.tg_id}\n"
        f"💰 Сумма: {value} ⭐\n"
        f"⚡ Проверьте и обработайте запрос."
    )

        await create_transaction(callback.from_user.id, value)
        await callback.message.answer(text, parse_mode='Markdown', disable_web_page_preview=True)
        await callback.message.delete()
        for admin_id in ADMIN:
            await bot.send_message(admin_id, message_text)
    else:
        await callback.answer('Не хватает',show_alert=True)



@user.callback_query(F.data == 'void')
async def fail_callback(callback: CallbackQuery):
    await callback.answer("❌ Неверно!")
    await callback.message.delete()


@user.message(F.text == 'test')
async def test_handler(message:Message,bot: Bot):
    check = await check_user(message.from_user.id)
    print(f'VASH STATUS: {check}')