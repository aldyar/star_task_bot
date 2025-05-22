from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command, CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.states import Date
from database.requests import get_today_users, get_all_users, get_all_users_date,get_top_referrers_by_date
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN
from datetime import datetime
from function.link_req import LinkFunction
import json  # обязательно в начале файла
from app.states import LinkStat

admin = Router()


class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in ADMIN

@admin.callback_query(F.data =='LinkStat')
async def link_stat_choose_handler(callback:CallbackQuery,state:FSMContext):
    await callback.message.delete()
    await callback.message.answer('*Выберите пункт*',parse_mode='Markdown',reply_markup=kb.inline_link_stat)
    await state.set_state(LinkStat.wait_name)


@admin.callback_query(F.data == 'CreateLink')
async def create_link_handler(callback:CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('*Напишите пожалуйста наименование ссылки английском языке без пробелом*\n _Пример_: `stat`',parse_mode='Markdown')


@admin.message(LinkStat.wait_name)
async def process_name_link(message:Message,state:FSMContext):
    name = message.text
    link_name = f'admin_{name}'
    await LinkFunction.set_link(link_name)
    await message.answer('✅ Ссылка успешно сохранена')
    await state.clear()


@admin.callback_query(F.data == 'LinkList')
async def link_list_handler(callback:CallbackQuery):
    await callback.message.delete()

    links = await LinkFunction.get_links()

    # создаем список списков кнопок
    buttons = [
        [InlineKeyboardButton(text=link.link_name, callback_data=link.link_name)]
        for link in links
    ]

    if not buttons:
        await callback.message.answer("Ссылки не найдены.")
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.answer("*Список ссылок:*",parse_mode='Markdown', reply_markup=keyboard)



@admin.callback_query(F.data.startswith('admin_'))
async def link_stat_handler(callback:CallbackQuery):
    link_name = callback.data
    await callback.answer()
    link = await LinkFunction.get_link(link_name)
    lang_dict = json.loads(link.lang) if link.lang else {}

    flyer_count = link.done_captcha - link.count_captcha
    
    total_lang_clicks = sum(lang_dict.values())
    geo_text = "\n".join(
        [f"— `{code}`: *{count}* ({round(count / total_lang_clicks * 100, 1)}%)"
         for code, count in lang_dict.items()]
    ) if total_lang_clicks else "Нет данных"
    text = f"""
*Статистика по ссылке* `{link.link_name}`

*Ссылка*: `https://t.me/FreeStard_bot?start={link.link_name}`

👤*Всего зашло*: *{link.clicks}*
✅*Прошли капчу: {link.done_captcha}* 
💎*Premium: {link.premium}*

🥏*Капча Flyer*: {flyer_count}
🤖*Капча бота*: {link.count_captcha}

🌍*GEO:*
{geo_text}"""
    
    await callback.message.answer(text,parse_mode='Markdown')