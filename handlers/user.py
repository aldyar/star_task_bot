from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from database.requests import (set_user, get_config, get_bonus_update, update_bonus, check_tasks, get_user, 
                                   get_withdraw_limit, set_referrer_id, create_transaction, get_task,
                                   is_user_subscribed,completed_task,create_task_completions_history,check_subscriptions,
                                   check_user,insert_message_id, count_reward,join_request,skip_task,get_task_about_taskid,test_fuck_func)
from function.task_req import get_first_available_task,skip_task_function,create_task_state,get_task_state,create_task_history,check_entry_task_history
from app.keyboards import withdraw_inline, withdraw_keyboard
from aiogram.enums import ChatAction
from aiogram import Bot
import random
from datetime import datetime, timedelta
import text as txt
user = Router()
from config import ADMIN, GROUP_ID,CHANNEL_ID,FLYER
from handlers.admin import start_admin
from aiogram import types
from aiogram.types import FSInputFile
import asyncio
from function.channel_req import StartChannelFunction as Channel
from handlers.user_subgram import test_subgram, test_subgram2
from function.subgram_req import SubGramFunction as Subgram
from app.storage import SubgramList
from app.storage import BotEntry, s_reward
from aiogram.types import ChatMember
from function.user_req import UserFunction 
from function.link_req import LinkFunction


image_start = 'images/image_start.jpg'
image_ref = 'images/image_ref.jpg'
image_withdraw = 'images/image_withdraw.jpg'
image_welcome = 'images/image_welcome.jpg'
image_task = 'images/image_task.jpg'

from flyerapi import Flyer
flyer = Flyer(FLYER)




@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext,bot:Bot):
    user = await get_user(message.from_user.id)
    if user:  # Если пользователь уже есть в базе данных
        await success_message(message,state)
        return
    

    if len(message.text.split()) > 1:
        referrer_id = message.text.split(maxsplit=1)[1]
        lang = message.from_user.language_code or "unknown"
        await state.update_data(lang = lang)
        await state.update_data(referrer_id=referrer_id)
        if referrer_id.startswith("admin_"):
            #lang = message.from_user.language_code or "unknown"
            ref_type = referrer_id.split("_", maxsplit=1)[1]
            premium = message.from_user.is_premium
            await LinkFunction.count_link(referrer_id,premium,lang,message.from_user.id)
    # if not await flyer.check(message.from_user.id,message.from_user.language_code): 
    #     return 
    
    subscribed = await is_user_subscribed(bot,message.from_user.id,CHANNEL_ID)
    if not subscribed:
    #СТАРАЯ КАПЧА            
        emoji, captcha = random.choice(kb.captchas)  # Выбираем случайную капчу
        channels = await Channel.get_channels()
        text = (
        "🤖 <b>Капча</b>\n\n"
        "🔵 Подпишись на <a href='https://t.me/FreeStards'>канал</a>\n\n"
    )
        if channels:
            for channel in channels:
                text += f"🔵 Подпишись на <a href='{channel.link}'>канал</a>\n"
            text += "\n"  # добавим отступ перед финальной частью
        text += (
        f"🔵 Нажми на {emoji} ниже, чтобы начать пользоваться ботом и получать звёзды,\n"
        "после прохождения начислим тебе 1⭐ на баланс бота:"
    )
        photo = FSInputFile(image_welcome)
        await message.answer_photo(photo,caption=text, reply_markup=captcha, parse_mode="HTML", disable_web_page_preview=True)
        return
    await success_message(message,state)

async def success_message(message: Message,state:FSMContext):
    text = await get_config('start_text')
    #image_url = await get_config('image_link')  # Получаем ссылку на изображение

    data = await state.get_data()
    referrer_id = data.get("referrer_id")
    lang = data.get('lang')
    await LinkFunction.count_done_captcha(referrer_id,message.from_user.id)
    username = message.from_user.username
    await set_user(message.from_user.id, username, referrer_id,lang)

    user_id = message.from_user.id
    referral_link = f"https://t.me/FreeStard_bot?start={user_id}"
    formatted_text = text.format(user_id=user_id,referral_link=referral_link)
    photo = FSInputFile(image_start)
    await message.answer_photo(photo, caption=formatted_text, parse_mode="HTML", reply_markup=kb.main)
    await message.answer(' *🎯Выполняй лёгкие задания и лутай халявные звёзды:*',parse_mode="Markdown", reply_markup=kb.task_inline)

    # if image_url:
    #     photo = FSInputFile(image_start)
    #     await message.answer_photo(photo, caption=formatted_text, parse_mode="HTML", reply_markup=kb.main)
    # else:
    #     await message.answer(formatted_text, parse_mode="HTML", reply_markup=kb.main,disable_web_page_preview=True)
    # await message.answer(' *🎯Выполняй лёгкие задания и лутай халявные звёзды:*',parse_mode="Markdown", reply_markup=kb.task_inline)



#ЗАДАНИЯ
@user.message(F.text == '🎯Задания')
async def get_task_hander(message: Message,state: FSMContext):
    user_id = message.from_user.id
    premium = int(message.from_user.is_premium or 0)
    name = message.from_user.first_name 
    user = await get_user(user_id)
    if not user.gender:
        await message.answer('*Пожалуйста, укажите ваш пол 👇*',parse_mode='Markdown',reply_markup=kb.inline_choose_gender)
        return
    if not await flyer.check(message.from_user.id,message.from_user.language_code):
        return
    try:
        subgram = await asyncio.wait_for(Subgram.send_post(user_id,name,premium,user.gender), timeout=3)
        links = await Subgram.get_unsubscribed_channel_links(subgram)
        SubgramList[user_id] = links
        unsubscribed_count = len(links)
        subgram_reward = unsubscribed_count * s_reward
        print(f'SUBGRAM REWARD:________{subgram_reward}')
        print(f'UNSUB:____________{unsubscribed_count}')
        print(f"[UPDATED] SubgramList for {user_id}: {SubgramList[user_id]}")
    except TimeoutError:
        SubgramList[user_id] = []
        subgram_reward = 0
        print(f"[TIMEOUT] Subgram request for {user_id} took too long.")

    task = await get_first_available_task(user_id)  # Получаем список доступных заданий
    photo =FSInputFile(image_task)
    if not task:
        #await message.answer('Заданий пока нет. Задания появятся в ближайшее время.')
        await test_subgram(message,state,user_id)
        return
    if task.type == 'subscribe':
        text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"

        if task.description:  # Проверяем, есть ли описание
            text += f"{task.description}\n\n"

        text += f"• <b>Подпишись на</b> <a href='{task.link}'>{task.link}</a>\n"
        text += f"• <b>Награда:</b> {task.reward}⭐"
        await state.update_data(task = task)
        task_reward = await count_reward(message.from_user.id)
        reward = task_reward + subgram_reward
        await message.answer_photo(photo,caption=f'*👑 Выполни все задания и получи* *{reward}⭐️!*\n\n'
                            '*🔻 Выполни текущее задание, чтобы открыть новое:*', parse_mode='Markdown')
        keyboard = await kb.complete_task_inline(task.link)
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
    elif task.type == 'entry':
        text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"

        if task.description:  # Проверяем, есть ли описание
            text += f"{task.description}\n\n"

        text += f"• <b>Подай заявку в канал</b> <a href='{task.link}'>{task.link}</a>\n"
        text += f"• <b>Награда:</b> {task.reward}⭐"
        await state.update_data(task = task)
        await create_task_state(user_id,task.id)
        task_reward = await count_reward(user_id)
        reward = task_reward + subgram_reward
        await message.answer_photo(photo,caption=f'*👑 Выполни все задания и получи* *{reward}⭐️!*\n\n'
                            '*🔻 Выполни текущее задание, чтобы открыть новое:*', parse_mode='Markdown')
        keyboard = await kb.entry_type_inline(task.link)
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
    elif task.type == 'BotEntry':
        text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"

        if task.description:  # Проверяем, есть ли описание
            text += f"{task.description}\n\n"

        text += f"• <b>Перейдите в бота</b> <a href='{task.link}'>{task.link}</a>\n"
        text += f"• <b>Награда:</b> {task.reward}⭐"
        await state.update_data(task = task)
        task_reward = await count_reward(user_id)
        reward = task_reward + subgram_reward
        await message.answer_photo(photo,caption=f'*👑 Выполни все задания и получи* *{reward}⭐️!*\n\n'
                            '*🔻 Выполни текущее задание, чтобы открыть новое:*', parse_mode='Markdown')
        keyboard = await kb.complete_task_inline(task.link)
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
        BotEntry[user_id] = False
        await asyncio.sleep(5)
        BotEntry[user_id] = True


#ЗАДАНИЯ
@user.callback_query(F.data == 'skip')
async def skip_task_handler(callback:CallbackQuery,state:FSMContext):
    await callback.message.delete()
    data = await state.get_data()
    task_present = data.get("task")
    task = await skip_task_function(callback.from_user.id,task_present.id)
    if not task:
        await callback.message.answer('Заданий пока нет. Задания появятся в ближайшее время.')
        return
    elif task == 3:
        return await test_subgram2(callback.message,state,callback.from_user.id)
    if task.type == 'subscribe':
    
        text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"

        if task.description:  # Проверяем, есть ли описание
            text += f"{task.description}\n\n"

        text += f"• <b>Подпишись на</b> <a href='{task.link}'>{task.link}</a>\n"
        text += f"• <b>Награда:</b> {task.reward}⭐"
        await state.update_data(task = task)
        keyboard = await kb.complete_task_inline(task.link)
        await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
    elif task.type == 'entry':
        text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"

        if task.description:  # Проверяем, есть ли описание
            text += f"{task.description}\n\n"

        text += f"• <b>Подай заявку в канал</b> <a href='{task.link}'>{task.link}</a>\n"
        text += f"• <b>Награда:</b> {task.reward}⭐"
        await state.update_data(task = task)
        await create_task_state(callback.from_user.id,task.id)
        keyboard = await kb.entry_type_inline(task.link)
        await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
    elif task.type == 'BotEntry':
        text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"

        if task.description:  # Проверяем, есть ли описание
            text += f"{task.description}\n\n"

        text += f"• <b>Перейдите в бота</b> <a href='{task.link}'>{task.link}</a>\n"
        text += f"• <b>Награда:</b> {task.reward}⭐"
        await state.update_data(task = task)
        reward = await count_reward(callback.from_user.id)
        
        keyboard = await kb.complete_task_inline(task.link)
        await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
        BotEntry[callback.from_user.id] = False
        await asyncio.sleep(5)
        BotEntry[callback.from_user.id] = True

#ЗАДАНИЯ
@user.callback_query(F.data == 'complete_task')
async def complete_task_handler(callback: CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    task_present = data.get("task")

    if not task_present:
        await callback.answer("Задание не найдено", show_alert=True)
        return

    chat_id = task_present.chat_id
    if task_present.type == 'BotEntry':
        entry_state = BotEntry.get(callback.from_user.id, False)
        if not entry_state:  # Если состояние False
            return await callback.answer("Задание не выполнено.")
    # Проверяем подписку только если задание типа "subscribe"
    if task_present.type == 'subscribe':
        is_subscribed = await is_user_subscribed(bot, callback.from_user.id, chat_id)
        if not is_subscribed:
            await callback.answer("Вы не подписаны на канал!", show_alert=True)
            return

    # Помечаем задание как выполненное
    completed = await completed_task(task_present.id, callback.from_user.id, task_present.reward)

    complete_text = (
        f'*✅ Задание №{task_present.id} выполнено!*\n\n'
        f'*• {task_present.reward}⭐️ начислено на ваш баланс в боте. Не отписывайтесь от канала в течение 7 дней, иначе звёзды будут обнулены!*'
    )
    await callback.message.answer(complete_text, parse_mode='Markdown')

    if completed:
        message_text = (
            f'🎯 *Задание №{task_present.id} завершено!*\n\n'
            f'• *Ссылка на задание:* [{task_present.link}]({task_present.link})\n'
            f'• *Количество выполнений:* {task_present.completed_count + 1}'
        )
        for admin_id in ADMIN:
            await bot.send_message(admin_id, message_text, parse_mode='Markdown', disable_web_page_preview=True)

    await callback.answer('⭐ Вознаграждение зачислено')
    await create_task_completions_history(callback.from_user.id, task_present.id)
    await callback.message.delete()

    # Получаем следующее задание
    task = await get_first_available_task(callback.from_user.id)
    await state.update_data(task=task)

    if not task:
        await test_subgram2(callback.message,state,callback.from_user.id)
        return

    # Отправляем новое задание
    text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"
    if task.description:
        text += f"{task.description}\n\n"

    if task.type == 'subscribe':
        text += f"• <b>Подпишись на</b> <a href='{task.link}'>{task.link}</a>\n"
        text += f"• <b>Награда:</b> {task.reward}⭐"
        keyboard = await kb.complete_task_inline(task.link)
    elif task.type == 'entry':
        text += f"• <b>Подай заявку в канал</b> <a href='{task.link}'>{task.link}</a>\n"
        text += f"• <b>Награда:</b> {task.reward}⭐"
        await create_task_state(callback.from_user.id, task.id)
        keyboard = await kb.entry_type_inline(task.link)
    elif task.type == 'BotEntry':
        text += f"• <b>Перейдите в бота</b> <a href='{task.link}'>{task.link}</a>\n"
        text += f"• <b>Награда:</b> {task.reward}⭐"
        keyboard = await kb.complete_task_inline(task.link)
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
    start_channel_subscribed = await Channel.is_user_subscribed(bot,callback.from_user.id)
    if subscribed and start_channel_subscribed:
        data = await state.get_data()
        referrer_id = data.get("referrer_id")
        lang = data.get('lang')
        
        await LinkFunction.count_done_our_captcha(referrer_id,callback.from_user.id)
        
        await callback.answer("✅ Верно! Доступ разрешен.")
        await callback.message.delete()
        user = await callback.bot.get_chat(callback.from_user.id)
        username = user.username 
        await set_user(callback.from_user.id, username, referrer_id,lang)
        text = await get_config('start_text')
        image_url = await get_config('image_link')  # Получаем ссылку на изображение
        user_id = callback.from_user.id
        referral_link = f"https://t.me/FreeStard_bot?start={user_id}"
        formatted_text = text.format(user_id=user_id,referral_link=referral_link)
        if image_url:
            photo = FSInputFile(image_url)
            await callback.message.answer_photo(photo, caption=formatted_text, parse_mode="HTML", reply_markup=kb.main)
        else:
            await callback.message.answer(formatted_text, parse_mode="HTML", reply_markup=kb.main,disable_web_page_preview=True)
            await callback.message.answer(' *🎯Выполняй лёгкие задания и лутай халявные звёзды:*',parse_mode="Markdown", reply_markup=kb.task_inline)
    else:
        await callback.answer("❌ Вы не подписаны на канал! Подпишитесь и попробуйте снова.",show_alert=True)


#ЗАДАНИЯ
@user.callback_query(F.data == 'task')
async def task_handler(callback:CallbackQuery, state:FSMContext):
    user_id = callback.from_user.id
    premium = int(callback.from_user.is_premium or 0)
    name = callback.from_user.first_name
    user = await get_user(user_id)
    if not user.gender:
        await callback.answer()
        await callback.message.answer('*Пожалуйста, укажите ваш пол 👇*',parse_mode='Markdown',reply_markup=kb.inline_choose_gender)
        return 
    if not await flyer.check(callback.from_user.id,callback.from_user.language_code):
        return
    try:
        subgram = await asyncio.wait_for(Subgram.send_post(user_id, name, premium,user.gender), timeout=3)
        links = await Subgram.get_unsubscribed_channel_links(subgram)
        SubgramList[user_id] = links
        unsubscribed_count = len(links)
        subgram_reward = unsubscribed_count * s_reward
        print(f"[UPDATED] SubgramList for {user_id}: {SubgramList[user_id]}")
    except TimeoutError:
        SubgramList[user_id] = []
        subgram_reward = 0
        print(f"[TIMEOUT] Subgram request for {user_id} took too long.")

    task = await get_first_available_task(callback.from_user.id)  # Получаем список доступных заданий

    if not task:
        #await callback.message.answer('Заданий пока нет. Задания появятся в ближайшее время.')
        await test_subgram(callback.message,state,callback.from_user.id)
        await callback.answer()
        return
    if task.type == 'subscribe':
        text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"

        if task.description:  # Проверяем, есть ли описание
            text += f"{task.description}\n\n"

        text += f"• <b>Подпишись на</b> <a href='{task.link}'>{task.link}</a>\n"
        text += f"• <b>Награда:</b> {task.reward}⭐"
        await state.update_data(task = task)
        task_reward = await count_reward(callback.from_user.id)
        reward = task_reward + subgram_reward
        await callback.message.answer(f'*👑 Выполни все задания и получи* *{reward}⭐️!*\n\n'
                            '*🔻 Выполни текущее задание, чтобы открыть новое:*', parse_mode='Markdown')
        keyboard = await kb.complete_task_inline(task.link)
        await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
    elif task.type == 'entry':
        text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"

        if task.description:  # Проверяем, есть ли описание
            text += f"{task.description}\n\n"

        text += f"• <b>Подай заявку в канал</b> <a href='{task.link}'>{task.link}</a>\n"
        text += f"• <b>Награда:</b> {task.reward}⭐"
        await state.update_data(task = task)
        await create_task_state(callback.from_user.id,task.id)
        task_reward = await count_reward(callback.from_user.id)
        reward = task_reward + subgram_reward
        await callback.message.answer(f'*👑 Выполни все задания и получи* *{reward}⭐️!*\n\n'
                            '*🔻 Выполни текущее задание, чтобы открыть новое:*', parse_mode='Markdown')
        keyboard = await kb.entry_type_inline(task.link)
        await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
    elif task.type == 'BotEntry':
        text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"

        if task.description:  # Проверяем, есть ли описание
            text += f"{task.description}\n\n"

        text += f"• <b>Перейдите в бота</b> <a href='{task.link}'>{task.link}</a>\n"
        text += f"• <b>Награда:</b> {task.reward}⭐"
        await state.update_data(task = task)
        task_reward = await count_reward(callback.from_user.id)
        reward = task_reward + subgram_reward
        
        keyboard = await kb.complete_task_inline(task.link)
        await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
        BotEntry[callback.from_user.id] = False
        await asyncio.sleep(5)
        BotEntry[callback.from_user.id] = True
    await callback.answer()



@user.message(F.text == '⭐️Заработать звёзды')
async def ref_system(message: Message):
    if not await flyer.check(message.from_user.id,message.from_user.language_code):
        return
    user_id = message.from_user.id
    referral_link = f"https://t.me/FreeStard_bot?start={user_id}"
    change_text = await get_config('ref_text')
    user = await get_user(user_id)
    text = (
    f"{change_text}\n\n"
    "<b>Ваша ссылка:</b>\n"
    f"<code>{referral_link}</code>\n\n"
    "❓ <b>Как использовать свою реферальную ссылку?</b>\n\n"
    "• <b>Отправь её друзьям в личные сообщения</b> 👥\n"
    "• <b>Поделись ссылкой в своём Telegram-канале</b> 📢\n"
    "• <b>Оставь её в комментариях или чатах</b> 💬\n"
    "• <b>Распространяй ссылку в соцсетях: TikTok, Instagram, WhatsApp и других</b> 🌐\n\n"
    f"🗣 <b>Вы пригласили:</b> {user.referral_count}"
)
    formatted_text = change_text.format(referral_link=referral_link)

    photo = FSInputFile(image_ref)
    await message.answer_photo(photo,caption=formatted_text, disable_web_page_preview=True, parse_mode='HTML')


@user.message(F.text == '🎁Вывести звёзды')
async def withdraw(message:Message):
    # if not await flyer.check(message.from_user.id,message.from_user.language_code):
    #     return
    user = await get_user(message.from_user.id)
    username = message.from_user.username
    await UserFunction.set_username(message.from_user.id,username)
    if not user.lang:
        lang = message.from_user.language_code or "unknown"
        await UserFunction.set_lang_user(message.from_user.id,lang)

    keyboard = await withdraw_keyboard()
    text = (
        f"*Заработано: {user.balance}⭐️*\n\n"
        '*🔻 Выбери, подарок за сколько звёзд хочешь получить:*'
    )
    photo = FSInputFile(image_withdraw)
    await message.answer_photo(photo,caption=text, parse_mode='Markdown', reply_markup=keyboard)



@user.callback_query(lambda c: c.data and c.data.startswith("withdraw_"))
async def handle_withdraw_callback(callback: CallbackQuery, bot: Bot):
    value = int(callback.data.removeprefix("withdraw_")) 
    user = await get_user(callback.from_user.id)
    username = callback.from_user.username
    await UserFunction.set_username(callback.from_user.id,username)
    if not user.username:
        return await callback.answer('Укажите пожалуйста username в профиле Telegram',show_alert=True)
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

        transaction = await create_transaction(callback.from_user.id, value,user.lang)

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


        # for admin_id in ADMIN:
        #     await bot.send_message(admin_id, message_text)
    else:
        amount = value - user.balance
        await callback.answer(f'Заработайте еще {amount}⭐, что бы получить подарок!',show_alert=True)


@user.callback_query(F.data.startswith('gender_'))
async def choose_gender_handler(callback:CallbackQuery):
    await callback.message.delete()
    gender = callback.data.removeprefix("gender_")
    await UserFunction.set_gender(callback.from_user.id,gender)
    await callback.message.answer('*Ваш пол сохранен, нажмите снова на кнопку 🎯Задания*',parse_mode='Markdown')


@user.callback_query(F.data == 'void')
async def fail_callback(callback: CallbackQuery):
    await callback.answer("❌ Неверно!")
    await callback.message.delete()


#TEST
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################

from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest



@user.message(F.text == "test")
async def check_admin_handler(message: Message, bot: Bot):
    result = await flyer.check(message.from_user.id,'ru')
    await message.answer(str(result))

@user.message(F.text == "test2")
async def check_admin_handler(message: Message, bot: Bot):
    await UserFunction.save_all()
    print('OK')

@user.message(F.text == 'lang')
async def test_lang(message:Message):
    lang = message.from_user.language_code or "unknown"
    await message.answer(f'{lang}')


@user.chat_join_request()
async def handle_join_request(update: types.ChatJoinRequest):
    user_id = update.from_user.id
    chat_id = update.chat.id
    task = await get_task_state(user_id)
    object = await get_task_about_taskid(task.task_id)
    check_history = await check_entry_task_history(user_id,object.id)
    if check_history:
        await create_task_history(user_id,object.id,chat_id)
        completed = await completed_task(object.id,user_id,object.reward)
        #await update.bot.send_message(chat_id=user_id, text=f'FIND TASK ID:{task.task_id}') 
        #complete = await join_request(user_id, chat_id)
        complete_text = (
                    f'*✅ Задание №{object.id} выполнено!*\n\n'
                    f'*• {object.reward}⭐️ начислено на ваш баланс в боте, не отписывайтесь от канала в течении 7 дней, иначе звёзды будут обнулены!!*'
                )
        await update.bot.send_message(chat_id=user_id, text=complete_text,parse_mode='Markdown',reply_markup=kb.next_task_inline)
    elif not check_history:
        await update.bot.send_message(chat_id=user_id,text = '*Задание выполнено, выберите другое задание*',parse_mode='Markdown',reply_markup=kb.next_task_inline)
    if completed:
            message_text = (f'🎯*Задание под номером  №*{object.id} *завершило работу*\n\n'
                            f'• *Ссылка на задание:* [{object.link}]({object.link})\n'
                            f'• *Колличество выполнений:* {object.completed_count+1}')
            for admin_id in ADMIN:
                await update.bot.send_message(admin_id, message_text,parse_mode='Markdown', disable_web_page_preview=True)


        



#@user.message(F.forward_from_chat)
async def testter(message:Message):
    if message.forward_from_chat:
            chat_title = message.forward_from_chat.title
            await message.answer(chat_title)