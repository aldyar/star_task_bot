from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command, CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.states import EditLimit
from app.database.requests import edit_withdraw_limit
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
    keyboard = await kb.withdraw_edit_req()
    await callback.message.delete()
    await callback.message.answer('*Выберите ячейку которую хотите изменить*',parse_mode='Markdown',reply_markup=keyboard)


@admin.callback_query(Admin(), F.data.startswith('editlimit_'))
async def edit_limit_handler(callback: CallbackQuery, state: FSMContext):
    value = int(callback.data.split('_')[1])
    column_mapping = [
    'withdraw_1',
    'withdraw_2',
    'withdraw_3',
    'withdraw_4',
    'withdraw_5',
    'withdraw_6',
    'withdraw_7',
]
    column_name = column_mapping[value - 1]
    await state.update_data(column_name=column_name, current_value=value)

    await callback.message.answer('✏️*Введите сумму которую хотите поменять:*')
    await callback.message.delete()
    await state.set_state(EditLimit.edit_withdraw_limit)


@admin.message(EditLimit.edit_withdraw_limit)
async def process_edit_limit_handler(message:Message, state: FSMContext):
    try:
        new_value = int(message.text)  # Проверяем, что введено число
    except ValueError:
        await message.answer('❌ Пожалуйста, введите числовое значение!')
        return

    data = await state.get_data()
    column_name = data.get('column_name')
    
    if not column_name:
        await message.answer('❌ Ошибка! Невозможно найти нужную колонку.')
        return

    # Вызываем нашу ORM функцию для изменения лимита
    await edit_withdraw_limit(column_name=column_name, new_value=new_value)

    await message.answer(f'✅ Лимит успешно изменён на {new_value}⭐️.')
    await state.clear()  # Очищаем состояние

    keyboard = await kb.withdraw_edit_req()
    await message.answer('*Выберите ячейку которую хотите изменить*',
        parse_mode='Markdown',
        reply_markup=keyboard
    )




@admin.callback_query(Admin(), F.data == 'withdraw_req')
async def withdraw_req_handler(callback: CallbackQuery):
    await callback.answer('WORKING')