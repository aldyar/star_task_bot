from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.database.requests import (set_user, get_config, get_bonus_update, update_bonus, check_tasks, get_user, 
                                   get_withdraw_limit, set_referrer_id, create_transaction, get_task,
                                   is_user_subscribed,completed_task,create_task_completions_history,check_subscriptions,
                                   check_user,insert_message_id, count_reward,join_request,skip_task,get_task_about_taskid)
from app.database.task_req import get_first_available_task,skip_task_function,create_task_state,get_task_state,create_task_history,check_entry_task_history
from app.keyboards import withdraw_inline, withdraw_keyboard
from aiogram import Bot
import random
from app.database.user_req import UserFunction as User
from app.user import success_message,ref_system
from aiogram.types import FSInputFile

image_stat = 'images/image_stat.jpg'

user = Router()


@user.message(F.text == '👤Профиль')
async def user_profile_handler(message:Message):
    user = await get_user(message.from_user.id)
    ref_week = await User.get_referral_count_by_days(message.from_user.id,7)
    referrals = await User.get_referral(message.from_user.id)
    text = f"""
✨ МОЯ СТАТИСТИКА
──────────────
👤 Имя: {user.username}
🆔 ID: {message.from_user.id}
──────────────
💰 Баланс: {user.balance}⭐️
👥 Всего рефералов: {user.referral_count}
📆 За неделю: {ref_week}
──────────────
📜 Реферальный список:
"""
    photo = FSInputFile(image_stat)
    # Если у пользователя есть рефералы
    if referrals:
        # Для каждого реферала формируем строку
        referral_list = "\n".join([f"@{referral.username} (ID: {referral.tg_id})" for referral in referrals])
        text += referral_list
    else:
        text += "Нет приглашённых пользователей."
    await message.answer_photo(photo,caption=text,reply_markup=kb.inline_user_profile)

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



    await callback.message.answer(text, disable_web_page_preview=True, parse_mode='HTML')
    await callback.answer()

