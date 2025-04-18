from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command, CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.states import Date
from app.database.requests import get_today_users, get_all_users, get_all_users_date,get_top_referrers_by_date
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN
from datetime import datetime

admin = Router()


class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in ADMIN
    

@admin.message(Admin(),F.text == 'Статистика')
async def statistics_handler(message: Message, state: FSMContext):
    await state.clear()
    users = await get_today_users()
    all_users = await get_all_users()
    
    total_users = len(users)
    total_all_users = len(all_users)
    
    # Отправляем главное сообщение со статистикой
    await message.answer(
        f"📊 Сегодняшняя статистика:\n\n"
        f"🔢 Общее количество пользователей: {total_all_users}\n"
        f"📊 Пользователей сегодня: {total_users}",
        reply_markup=kb.stat_edit
    )

    # Отправляем каждого пользователя отдельным сообщением
    for user in users:
        username = user.username if user.username else "Не указан"
        referrer_id = user.referrer_id if user.referrer_id else "Нет"
        
        user_info = (
            f"👤 Username: `{username}`\n"
            f"🆔 Telegram ID: {user.tg_id}\n"
            f"📲 Referrer ID: {referrer_id}\n"
            f"📊 Приглашенных: {user.referral_count}"
        )
        
        await message.answer(user_info,parse_mode='Markdown')

@admin.callback_query(Admin(), F.data.startswith('NumDate_'))
async def num_date_handler(callback: CallbackQuery, state: FSMContext):
    type = callback.data.removeprefix("NumDate_")
    await state.update_data(type=type) 
    today_date = datetime.now().strftime('%d-%m-%Y')
    
    text = (
        "📅 Пожалуйста, введите первую дату в формате: *дд-мм-гггг*\n"
        f"📌 Пример сегодняшней даты: `{today_date}`"
    )
    
    await callback.message.answer(text, parse_mode='Markdown')
    await state.set_state(Date.first_date)
    await callback.answer()


@admin.message(Date.first_date)
async def process_first_date_handler(message: Message, state: FSMContext):
    date_1 = message.text.strip()
    today_date = datetime.now().strftime('%d-%m-%Y')
    await state.update_data(date_1=date_1)  # Сохраняем первую дату в состоянии    today_date = datetime.now().strftime('%d-%m-%Y')

    text = (
        "📅 Пожалуйста, введите вторую дату в формате: *дд-мм-гггг*\n"
        f"📌 Пример сегодняшней даты: `{today_date}`"
    )
    await message.answer(text,parse_mode='Markdown')
    await state.set_state(Date.second_date)


@admin.message(Date.second_date)
async def process_second_date_handler(message:Message,state: FSMContext):
    date_2 = message.text.strip()
    await state.update_data(date_2=date_2)  # Сохраняем первую дату в состоянии
    # Теперь получаем сохранённые данные из состояния
    data = await state.get_data()
    date_1 = data.get("date_1")
    type = data.get("type")
    # Ответ с подтверждением
    await message.answer(
        f"✅ Вы ввели даты:\n\n"
        f"📅 Первая дата: `{date_1}`\n"
        f"📅 Вторая дата: `{date_2}`",
        parse_mode='Markdown'
    )
    #users = await get_all_users()
    if type == 'reg':
        users = await get_all_users_date(date_1, date_2)
        for user in users:
            username = user.username if user.username else "Не указан"
            referrer_id = user.referrer_id if user.referrer_id else "Нет"
            
            user_info = (
                f"👤 Username: @{username}\n"
                f"🆔 Telegram ID: {user.tg_id}\n"
                f"📲 Referrer ID: {referrer_id}\n"
                f"📊 Приглашенных: {user.referral_count}"
            )
            
            await message.answer(user_info, parse_mode='Markdown')
        # Сбрасываем состояние после завершения
    elif type == 'ref':
        result = await get_top_referrers_by_date(date_1, date_2)
        response_text = f"🏆 Топ рефов с {date_1.replace('-', '.')} по {date_2.replace('-', '.')}:\n\n"
        
        if result:
            for row in result:
                display_name = f"@{row[1]}" if row[1] else f"ID: {row[0]}"
                response_text += f"{display_name} — {row[2]} приглашений\n"
        else:
            response_text += "Нет рефералов в этом промежутке."

        await message.answer(response_text)
    await state.clear()


