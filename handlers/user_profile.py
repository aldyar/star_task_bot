from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from database.requests import (set_user, get_config, get_bonus_update, update_bonus, check_tasks, get_user, 
                                   get_withdraw_limit, set_referrer_id, create_transaction, get_task,
                                   is_user_subscribed,completed_task,create_task_completions_history,check_subscriptions,
                                   check_user,insert_message_id, count_reward,join_request,skip_task,get_task_about_taskid)
from function.task_req import get_first_available_task,skip_task_function,create_task_state,get_task_state,create_task_history,check_entry_task_history
from app.keyboards import withdraw_inline, withdraw_keyboard
from aiogram import Bot
import random
from function.user_req import UserFunction as User
from handlers.user import success_message,ref_system
from aiogram.types import FSInputFile
from function.mini_adds_req import MiniAdds as MiniAddsFunction
from handlers.user_check import subgram_captcha
import asyncio
from app.states import Promocode
from function.promocode_req import PromocodeFunction

image_stat = 'images/image_stat.jpg'

user = Router()


@user.message(F.text == '👤Профиль')
async def user_profile_handler(message:Message|CallbackQuery,state:FSMContext):
    await state.clear()
    from handlers.user import add_keyboard_handler
    type = 'profile'
    user = await get_user(message.from_user.id)
    reply_target = message.message if isinstance(message, CallbackQuery) else message

    if not user.gender:
        await reply_target.answer('*Пожалуйста, укажите ваш пол 👇*',parse_mode='Markdown',reply_markup=kb.inline_choose_gender)
        return
    
    if not await subgram_captcha(message,type):
        return
    

    # mini_add_base_list  = await MiniAddsFunction.get_mini_add('base')
    # if mini_add_base_list:
    #     mini_add_base = random.choice(mini_add_base_list)
    #     keyboard = await kb.mini_add(mini_add_base.button_text,mini_add_base.url)
    #     await reply_target.answer(mini_add_base.text,parse_mode='HTML',reply_markup=keyboard)
    #     await asyncio.sleep(1)


    # 🔀 Случайный выбор: 50% базовая реклама, 50% кнопка "подарок"
    mini_add_base_list = await MiniAddsFunction.get_mini_add('base')
    if mini_add_base_list and random.choice([True, False]):
        # Показываем базовую рекламу
        mini_add_base = random.choice(mini_add_base_list)
        keyboard = await kb.mini_add(mini_add_base.button_text, mini_add_base.url)
        await reply_target.answer(mini_add_base.text, parse_mode='HTML', reply_markup=keyboard)
        await asyncio.sleep(1)
    else:
        # Показываем клавиатуру "Выберите подарок"
        await add_keyboard_handler(message)

    
    
    ref_week = await User.get_referral_count_by_days(message.from_user.id,7)
    referrals = await User.get_referral(message.from_user.id)
    text = f"""
✨ МОЯ СТАТИСТИКА
──────────────
👤 Имя: {user.username}
🆔 ID: {message.from_user.id}
──────────────
💰 Баланс: {user.balance:.2f}⭐️
👥 Всего рефералов: {user.referral_count}
📆 За неделю: {ref_week}
"""
    photo = FSInputFile(image_stat)
    # Если у пользователя есть рефералы
    # if referrals:
    #     # Для каждого реферала формируем строку
    #     referral_list = "\n".join([f"@{referral.username} (ID: {referral.tg_id})" for referral in referrals])
    #     text += referral_list
    # else:
    #     text += "Нет приглашённых пользователей."
    await reply_target.answer_photo(photo,caption=text,reply_markup=kb.inline_user_profile)


@user.callback_query(F.data =='BackMenu')
async def back_user_handler(callback:CallbackQuery):
    await success_message(callback.message)
    await callback.answer()


@user.callback_query(F.data == 'EarnStars')
async def earn_stars_handler(callback:CallbackQuery):
    user_id = callback.from_user.id
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


    await callback.message.answer(formatted_text, disable_web_page_preview=True, parse_mode='HTML')
    await callback.answer()

@user.callback_query(F.data == 'UsePromocode')
async def use_promocode_handler(callback:CallbackQuery,state:FSMContext):
    await callback.answer()
    await callback.message.answer('🧾*Введите промокод*',parse_mode='Markdown')
    await state.set_state(Promocode.use_promo)


@user.message(Promocode.use_promo)
async def use_promocode_process(message:Message,state:FSMContext):
    code = message.text
    promo = await PromocodeFunction.get_promo(code)
    promocode = await PromocodeFunction.use_promocode(code, message.from_user.id)

    if promocode == 1:
        text = f'*Промокод не найден* `{code}`'
    if promocode == 2:
        text = f'*Промокод* `{code}` *не действителен*'
    if promocode == 3:
        text = f'*Вы уже использовали промокод* `{code}`'
    if promocode == 5:
        text = f'*✅Промокод успешно активирован, вам начислено ⭐️{promo.reward} *'
        

    await message.answer(text,parse_mode='Markdown')
    await state.clear()