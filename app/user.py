from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.database.requests import (set_user, get_config, get_bonus_update, update_bonus, check_tasks, get_user, 
                                   get_withdraw_limit, set_referrer_id, create_transaction, get_task,
                                   is_user_subscribed,completed_task,create_task_completions,check_subscriptions,
                                   check_user,insert_message_id, count_reward,join_request,skip_task)
from app.database.task_req import get_first_available_task,skip_task_function
from app.keyboards import withdraw_inline, withdraw_keyboard
from aiogram.enums import ChatAction
from aiogram import Bot
import random
from datetime import datetime, timedelta
import text as txt
user = Router()
from config import ADMIN, GROUP_ID,CHANNEL_ID
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
    start =   (
        "👋 *Добро пожаловать!*\n"
        "В нашем боте можно бесплатно зарабатывать звёзды, мы вывели уже более *250 тысяч звёзд*, посмотри –\n"
        "[🔗 https://t.me/FreeStard](https://t.me/FreeStard)\n\n"
        "🎁 *За регистрацию в боте, дарим тебе первую* `1⭐`, *получай больше звёзд этими способами:*\n"
        "• 🎯 *Выполняй задания*\n"
        "• 💎 *Забирай ежедневный бонус*\n"
        "• 👥 *Приглашай друзей по ссылке и получай по* `2⭐` *за каждого, просто отправь её другу:*\n"
        f"[🔗 https://t.me/FreeStard_bot?start={message.from_user.id}](https://t.me/FreeStard_bot?start={message.from_user.id})\n\n"
        "*Как только заработаешь минимум* `15⭐`, *выводи их в разделе* «💰 *Вывести звёзды*», *мы отправим тебе подарок за выбранное количество звёзд, удачи!*\n\n"
        )
    await message.answer(start,parse_mode="Markdown", reply_markup=kb.main, disable_web_page_preview=True)
    await message.answer(' *🎯Выполняй лёгкие задания и лутай халявные звёзды:*',parse_mode="Markdown", reply_markup=kb.task_inline)



@user.message(F.text == '🎯Задания')
async def get_task_hander(message: Message,state: FSMContext):
    task = await get_first_available_task(message.from_user.id)  # Получаем список доступных заданий

    if not task:
        await message.answer('Заданий пока нет. Задания появятся в ближайшее время.')
        return
    if task.type == 'subscribe':
        text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"
        
        if task.description:  # Проверяем, есть ли описание
            text += f"{task.description}\n\n"

        text += f"•<b> Подпишись на <a href='{task.link}'>{task.link}</a></b>\n"
        text += f"•<b> Награда: {task.reward}⭐</b>"
        await state.update_data(task = task)
        reward = await count_reward(message.from_user.id)
        await message.answer(f'*👑 Выполни все задания и получи* *{reward}⭐️!*\n\n'
                            '*🔻 Выполни текущее задание, чтобы открыть новое:*', parse_mode='Markdown')
        keyboard = await kb.complete_task_inline(task.link)
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
    elif task.type == 'entry':
        text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"
        
        if task.description:  # Проверяем, есть ли описание
            text += f"{task.description}\n\n"

        text += f"•<b> Подай заявку в канал <a href='{task.link}'>{task.link}</a></b>\n"
        text += f"•<b> Награда: {task.reward}⭐</b>"
        await state.update_data(task = task)
        reward = await count_reward(message.from_user.id)
        await message.answer(f'*👑 Выполни все задания и получи* *{reward}⭐️!*\n\n'
                            '*🔻 Выполни текущее задание, чтобы открыть новое:*', parse_mode='Markdown')
        keyboard = await kb.entry_type_inline(task.link)
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)



@user.callback_query(F.data == 'skip')
async def skip_task_handler(callback:CallbackQuery,state:FSMContext):
    await callback.message.delete()
    data = await state.get_data()
    task_present = data.get("task")
    task = await skip_task_function(callback.from_user.id,task_present.id)
    if not task:
        await callback.message.answer('Заданий пока нет. Задания появятся в ближайшее время.')
        return
    if task.type == 'subscribe':
    
        text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"
        
        if task.description:  # Проверяем, есть ли описание
            text += f"{task.description}\n\n"

        text += f"•<b> Подпишись на <a href='{task.link}'>{task.link}</a></b>\n"
        text += f"•<b> Награда: {task.reward}⭐</b>"
        keyboard = await kb.complete_task_inline(task.link)
        await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
    elif task.type == 'entry':
        text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"
        
        if task.description:  # Проверяем, есть ли описание
            text += f"{task.description}\n\n"

        text += f"•<b> Подай заявку в канал <a href='{task.link}'>{task.link}</a></b>\n"
        text += f"•<b> Награда: {task.reward}⭐</b>"
        keyboard = await kb.entry_type_inline(task.link)
        await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)



@user.callback_query(F.data == 'complete_task')
async def complete_task_handler(callback:CallbackQuery,bot:Bot,state:FSMContext):
    data = await state.get_data()
    task_present = data.get("task")
    
    chat_id = task_present.chat_id
    is_subscribed  = await is_user_subscribed(bot,callback.from_user.id,chat_id)
    if is_subscribed :
        copmpleted = await completed_task(task_present.id, callback.from_user.id, task_present.reward)
        complete_text = (
                f'*✅ Задание №{task_present.id} выполнено!*\n\n'
                f'*• {task_present.reward}⭐️ начислено на ваш баланс в боте, не отписывайтесь от канала в течении 7 дней, иначе звёзды будут обнулены!!*'
                )
        await callback.message.answer(complete_text,parse_mode='Markdown')
        if copmpleted:
            message_text = (f'🎯*Задание под номером  №*{task_present.id} *завершило работу*\n\n'
                            f'• *Ссылка на задание:* [{task_present.link}]({task_present.link})\n'
                            f'• *Колличество выполнений:* {task_present.completed_count+1}')
            for admin_id in ADMIN:
                await bot.send_message(admin_id, message_text,parse_mode='Markdown', disable_web_page_preview=True)
        await callback.answer('⭐Вознаграждения зачислено')
        await create_task_completions(callback.from_user.id,task_present.id)
        await callback.message.delete()
        task = await get_first_available_task(callback.from_user.id)  # Получаем список доступных заданий
        await state.update_data(task = task)

        if not task:
            await callback.message.answer('Заданий пока нет. Задания появятся в ближайшее время.')
            return



        if task.type == 'subscribe':
    
            text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"
            
            if task.description:  # Проверяем, есть ли описание
                text += f"{task.description}\n"

            text += f"•<b> Подпишись на <a href='{task.link}'>{task.link}</a></b>\n"
            text += f"•<b> Награда: {task.reward}⭐</b>"
            keyboard = await kb.complete_task_inline(task.link)
            await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
        elif task.type == 'entry':
            text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"
            
            if task.description:  # Проверяем, есть ли описание
                text += f"{task.description}\n"

            text += f"•<b> Подай заявку в канал <a href='{task.link}'>{task.link}</a></b>\n"
            text += f"•<b> Награда: {task.reward}⭐</b>"
            keyboard = await kb.entry_type_inline(task.link)
            await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)





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
async def success_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    subscribed = await is_user_subscribed(bot,callback.from_user.id,CHANNEL_ID)
    if subscribed:
        data = await state.get_data()
        referrer_id = data.get("referrer_id")
        await callback.answer("✅ Верно! Доступ разрешен.")
        await callback.message.delete()
        user = await callback.bot.get_chat(callback.from_user.id)
        username = user.username 
        await set_user(callback.from_user.id, username, referrer_id)
        start =   (
            "👋 *Добро пожаловать!*\n"
            "В нашем боте можно бесплатно зарабатывать звёзды, мы вывели уже более *250 тысяч звёзд*, посмотри –\n"
            "[🔗 https://t.me/FreeStard](https://t.me/FreeStard)\n\n"
            "🎁 *За регистрацию в боте, дарим тебе первую* `1⭐`, *получай больше звёзд этими способами:*\n"
            "• 🎯 *Выполняй задания*\n"
            "• 💎 *Забирай ежедневный бонус*\n"
            "• 👥 *Приглашай друзей по ссылке и получай по* `2⭐` *за каждого, просто отправь её другу:*\n"
            f"[🔗 https://t.me/FreeStard_bot?start={callback.from_user.id}](https://t.me/FreeStard_bot?start={callback.from_user.id})\n\n"
            "*Как только заработаешь минимум* `15⭐`, *выводи их в разделе* «💰 *Вывести звёзды*», *мы отправим тебе подарок за выбранное количество звёзд, удачи!*\n\n"
            )
        await callback.message.answer(start,parse_mode="Markdown", reply_markup=kb.main, disable_web_page_preview=True)
        await callback.message.answer(' *🎯Выполняй лёгкие задания и лутай халявные звёзды:*',parse_mode="Markdown", reply_markup=kb.task_inline)
    else:
        await callback.answer("❌ Вы не подписаны на канал! Подпишитесь и попробуйте снова.",show_alert=True)

@user.callback_query(F.data == 'task')
async def task_handler(callback:CallbackQuery, state:FSMContext):
    task = await get_first_available_task(callback.from_user.id)  # Получаем список доступных заданий

    if not task:
        await callback.message.answer('Заданий пока нет. Задания появятся в ближайшее время.')
        await callback.answer()

        return

    text = (
        f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"
        f"•<b> Подпишись на <a href='{task.link}'>{task.link}</a></b>\n"
        f"•<b> Награда: {task.reward}⭐</b>"
    )
    await state.update_data(task = task)
    reward = await count_reward(callback.from_user.id)
    await callback.message.answer(f'*👑 Выполни все задания и получи* *{reward}⭐️!*\n\n'
                         '*🔻 Выполни текущее задание, чтобы открыть новое:*', parse_mode='Markdown')
    keyboard = await kb.complete_task_inline(task.link)
    await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
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
    "*Следить за статусом своей заявки можно в нашем чате выводов в реальном времени:* [https://t.me/vyvod_star](https://t.me/vyvod_star)\n\n"
    "_Не меняйте @username, иначе мы не сможем отправить подарок, а заявка будет отклонена!_"
)
        message_text = (
        f"📢 Новая заявка на вывод!\n\n"
        f"👤 Пользователь: {user.username or 'Не указан'}\n"
        f"🆔 TG ID: {user.tg_id}\n"
        f"💰 Сумма: {value} ⭐\n"
        f"⚡ Проверьте и обработайте запрос."
    )

        transaction = await create_transaction(callback.from_user.id, value)

        # Сообщение для группы
        group_message = (
            f"*⏳ Новая заявка №{transaction.id} на получение подарка за {value}⭐* "
            f"*от пользователя *[{user.username}](http://t.me/{user.username})"
        )

        await callback.message.answer(text, parse_mode='Markdown', disable_web_page_preview=True)
        await callback.message.delete()

        # Отправка сообщения в группу
        #GROUP_ID = -1002430935554  # Заменить на ID твоей группы
        send_message = await bot.send_message(GROUP_ID, group_message, parse_mode='Markdown', disable_web_page_preview=True)
        await insert_message_id(transaction.id,send_message.message_id)


        for admin_id in ADMIN:
            await bot.send_message(admin_id, message_text)
    else:
        await callback.answer('Не хватает',show_alert=True)



@user.callback_query(F.data == 'void')
async def fail_callback(callback: CallbackQuery):
    await callback.answer("❌ Неверно!")
    await callback.message.delete()


#TEST
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################



@user.message(F.text == ("test"))
async def check_admin_handler(message: Message, bot: Bot):
    chat_id = -1001751157582  # ID канала, на который проверяем подписку
    user_id = message.from_user.id
    is_subscribed = await is_user_subscribed(chat_id, user_id, bot)
    if is_subscribed:
        print("Пользователь подписан на канал.")
    else:
        print("Пользователь НЕ подписан на канал.")

from aiogram import Bot
from aiogram.types import ChatMember
from aiogram.exceptions import TelegramBadRequest
async def is_user_subscribed_handler(chat_id: int, user_id: int,bot:Bot) -> bool:
    try:
        member: ChatMember = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        print(f"Статус пользователя: {member.status}")
        # Проверяем статус пользователя
        return member.status in ['member', 'administrator', 'creator']
    except TelegramBadRequest:
        # Если возникла ошибка, значит пользователь не подписан
        return False
    
    

YOUR_CHANNEL_ID = -1002503607464

from aiogram import types


@user.chat_join_request()
async def handle_join_request(update: types.ChatJoinRequest,state:FSMContext):
    data = await state.get_data()
    task = data.get("task")
    
    user_id = update.from_user.id
    channel_id = update.chat.id

    complete = await join_request(user_id, channel_id)
    if complete:
        complete_text = (
                f'*✅ Задание выполнено!*\n\n'
                f'*• Можете продолжать выполнения заданий*'
                )
    await update.bot.send_message(chat_id=user_id, text=complete_text,parse_mode='Markdown',reply_markup=kb.next_task_inline)    

        



#@user.message(F.forward_from_chat)
async def testter(message:Message):
    if message.forward_from_chat:
            chat_title = message.forward_from_chat.title
            await message.answer(chat_title)