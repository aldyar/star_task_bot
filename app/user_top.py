from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.database.requests import (set_user, get_config, get_bonus_update, update_bonus, check_tasks, get_user, 
                                   get_withdraw_limit, set_referrer_id, create_transaction, get_task,
                                   is_user_subscribed,completed_task,create_task_completions_history,check_subscriptions,
                                   check_user,insert_message_id, count_reward,join_request,skip_task,get_task_about_taskid)
from app.database.task_req import get_first_available_task,skip_task_function,create_task_state,get_task_state,create_task_history,check_entry_task_history
from aiogram.enums import ChatAction
from aiogram import Bot
from datetime import datetime, timedelta
from app.database.user_req import UserFunction
user = Router()
from aiogram.types import FSInputFile

image_url = 'images\image_top.jpg'
photo = FSInputFile(image_url)


@user.message(F.text == '🏆Топ')
async def top_handler(message: Message):

    top_users = await UserFunction.get_user_top_5_referrers(1)

    medals = ["🥇", "🥈", "🥉", "✨", "✨"]
    text = "🏆 <b>Топ-5 рефералов за день:</b>\n\n"

    user_in_top = False

    for i, (tg_id, username, count) in enumerate(top_users):
        # Если текущий юзер в списке
        if tg_id == message.from_user.id:
            user_in_top = True

        name = username if username != "Без username" else "."
        text += f"{medals[i]} <b>{name}</b> | Рефералов: <b>{count}</b>\n"

    if not user_in_top:
        my_count = await UserFunction.get_user_refferal_count(message.from_user.id,1)

        text += f"\n❌ Ты не в Топ-5 за 24 часа! | <b>{my_count}</b> рефералов."
    await message.answer_photo(photo, caption=text, parse_mode="HTML", reply_markup=kb.inline_user_top)



@user.callback_query(F.data == 'TopWeek')
async def top_handler(callback: CallbackQuery):

    top_users = await UserFunction.get_user_top_5_referrers(7)

    medals = ["🥇", "🥈", "🥉", "✨", "✨"]
    text = "🏆 <b>Топ-5 рефералов за неделю:</b>\n\n"

    user_in_top = False

    for i, (tg_id, username, count) in enumerate(top_users):
        # Если текущий юзер в списке
        if tg_id == callback.from_user.id:
            user_in_top = True

        name = username if username != "Без username" else "."
        text += f"{medals[i]} <b>{name}</b> | Рефералов: <b>{count}</b>\n"

    if not user_in_top:
        my_count = await UserFunction.get_user_refferal_count(callback.from_user.id,7)

        text += f"\n❌ Ты не в Топ-5 за неделю! | <b>{my_count}</b> рефералов."

    await callback.message.answer_photo(photo, caption=text, parse_mode="HTML")
    await callback.message.delete()


@user.callback_query(F.data == 'TopMonth')
async def top_handler(callback: CallbackQuery):

    top_users = await UserFunction.get_user_top_5_referrers(30)

    medals = ["🥇", "🥈", "🥉", "✨", "✨"]
    text = "🏆 <b>Топ-5 рефералов за месяц:</b>\n\n"

    user_in_top = False

    for i, (tg_id, username, count) in enumerate(top_users):
        # Если текущий юзер в списке
        if tg_id == callback.from_user.id:
            user_in_top = True

        name = username if username != "Без username" else "."
        text += f"{medals[i]} <b>{name}</b> | Рефералов: <b>{count}</b>\n"

    if not user_in_top:
        my_count = await UserFunction.get_user_refferal_count(callback.from_user.id,30)

        text += f"\n❌ Ты не в Топ-5 за месяц! | <b>{my_count}</b> рефералов."

    await callback.message.answer_photo(photo, caption=text, parse_mode="HTML")
    await callback.message.delete()



    