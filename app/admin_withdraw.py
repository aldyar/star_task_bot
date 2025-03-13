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

admin = Router()


class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in ADMIN
    

@admin.message(Admin(), F.text == 'Вывод средств')
async def withdraw_hander(message: Message):
    text = ('*В этой панели вы можете изменить суммы вывода ⭐️ или посмотреть заявки на вывод*')
    await message.answer(text, parse_mode='Markdown', reply_markup=kb.withdraw_menu_admin)


@admin.callback_query(Admin(), F.data == 'editwithdraw_limit')
async def edit_withdraw_limit_handler(callback: CallbackQuery):
    await callback.answer('WORK')


@admin.callback_query(Admin(), F.data == 'withdraw_req')
async def edit_withdraw_limit_handler(callback: CallbackQuery):
    await callback.answer('WORKING')