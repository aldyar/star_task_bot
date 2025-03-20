from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command, CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.states import EditBonus
from app.database.requests import get_config, edit_bonus
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN

admin = Router()


class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in ADMIN
    

@admin.message(Admin(), F.text == 'Бонус')
async def edit_bonus_handler(message: Message,state:FSMContext):
    await state.clear()
    bonus = await get_config('bonus_amount')
    await message.answer(f'*Сумма ежедевного бонуса*: {bonus}', parse_mode='Markdown',reply_markup=kb.edit_bonus)


@admin.callback_query(Admin(),F.data == 'editbonus')
async def process_edit_bonus_handler(callback:CallbackQuery,state: FSMContext):
    await callback.message.answer('*Введите новую сумму бонуса:*', parse_mode='Markdown')
    await state.set_state(EditBonus.edit_bonus)

@admin.message(EditBonus.edit_bonus)
async def state_edit_bonus(message: Message, state: FSMContext):
    bonus_amount = float(message.text)
    await edit_bonus(bonus_amount)
    await message.answer('*Сумма бонусов успешно обновлена*')

