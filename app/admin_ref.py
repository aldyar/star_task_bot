from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command, CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.states import EditRef
import re
from app.database.requests import get_config, edit_ref_text, edit_ref_reward
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN
from aiogram.utils.text_decorations import html_decoration

admin = Router()


class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in ADMIN
    

@admin.message(Admin(),F.text == 'Реферальная система')
async def referal_system(message: Message,state:FSMContext):
    await state.clear()
    text = await get_config('ref_text')
    reward = await get_config('ref_reward')

    message_text = (
        '*Ваш текст:*\n\n'
        f'{text}\n\n'
        f'*Сумма вознаграждения: {reward}*'
    )

    await message.answer(message_text,parse_mode='Markdown',reply_markup=kb.referal_menu)


@admin.callback_query(Admin(),F.data == 'edit_ref_text')
async def edit_text(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "✏️ Введите новый текст для реферальной системы."
    ,parse_mode='Markdown')
    await callback.answer()
    await state.set_state(EditRef.edit_ref_text)

@admin.message(EditRef.edit_ref_text)
async def process_edit(message: Message, state: FSMContext):
    text_with_html = html_decoration.unparse(message.text, message.entities)
    await edit_ref_text(text_with_html)
    await state.clear()
    await message.answer('✅Текст успешно сохранен')




@admin.callback_query(Admin(),F.data == 'edit_ref_reward')
async def edit_reward(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('⭐️Введите новую сумму вознаграждения:')
    await callback.answer()
    await state.set_state(EditRef.edit_ref_reward)


@admin.message(EditRef.edit_ref_reward)
async def process_edit(message: Message, state: FSMContext):
    reward = message.text.strip()
    await edit_ref_reward(reward)
    await state.clear()
    await message.answer('⭐️Сумма вознаграждения успешно изменено')