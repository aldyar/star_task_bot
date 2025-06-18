from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command, CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.states import EditLimit
from database.requests import edit_withdraw_limit, get_pending_transactions, complete_transaction, get_transaction
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN, GROUP_ID
from aiogram import Bot
import asyncio
from aiogram.utils.text_decorations import markdown_decoration as md


admin = Router()


class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in ADMIN
    

@admin.message(Admin(), F.text == 'Вывод средств')
async def withdraw_hander(message: Message,state:FSMContext):
    await state.clear()
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
    await state.clear()

    keyboard = await kb.withdraw_edit_req()
    await message.answer('*Выберите ячейку которую хотите изменить*',
        parse_mode='Markdown',
        reply_markup=keyboard
    )




@admin.callback_query(Admin(), F.data == 'withdraw_req')
async def withdraw_req_handler(callback: CallbackQuery):
    withdrawals = await get_pending_transactions()  # Получаем список заявок (функция из базы)

    if not withdrawals:
        await callback.message.answer("Нет заявок на вывод.")
        await callback.answer()
        return

    for withdrawal in withdrawals:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Выполнить", callback_data=f"complete_withdraw_{withdrawal.id}")]
            ]
        )

        message_text = (
            f"📌 *Заявка №{withdrawal.id}*\n"
            f"👤 *Пользователь:* {md.quote('@' + (withdrawal.username or 'Не указан'))}\n"
            f"🆔 *TG ID:* `{withdrawal.tg_id}`\n"
            f"🌍 *GEO:* {withdrawal.user_lang}\n"
            f"💰 *Сумма:* `{withdrawal.amount} ⭐️`\n"
            f"🎁 *Подарок:* {withdrawal.emoji}\n"
            f"⏳ *Статус:* _Ожидает выполнения_"
        )

        await callback.message.answer(message_text, reply_markup=keyboard, parse_mode="Markdown")
        await asyncio.sleep(0.3)  # защита от FloodWait

    await callback.answer()  # Закрываем callback


@admin.callback_query(Admin(), F.data.startswith("complete_withdraw_"))
async def complete_withdraw(callback: CallbackQuery, bot: Bot):
    """Обрабатывает нажатие на кнопку выполнения заявки."""
    withdraw_id = int(callback.data.split("_")[-1])  # Получаем ID заявки
    print(f'VASH IIIIIID:{withdraw_id}')
    success = await complete_transaction(withdraw_id)  # Отмечаем заявку выполненной в БД
    transaction = await get_transaction(withdraw_id)
    if success:
        await bot.send_message(
            GROUP_ID,
            f"*✅ #Заявка_{transaction.id} выполнена, отправили подарок за {transaction.amount}⭐️({transaction.emoji}).*\n\n"
            '*Создать заявку: @FreeStard_bot*',
            reply_to_message_id=transaction.message_id, parse_mode='Markdown'
        )
        await callback.message.delete()
        updated_text = (
            f"📌 *Заявка №{transaction.id}*\n"
            f"👤 *Пользователь:* `{transaction.username or 'Не указан'}`\n"
            f"🆔 *TG ID:* `{transaction.tg_id}`\n"
            f"💰 *Сумма:* `{transaction.amount} ⭐️`\n"
            f"✅ *Статус:* Выполнено"
        )
        await callback.message.answer(updated_text, parse_mode="Markdown")
        await callback.answer("Заявка успешно выполнена! ✅")
    else:
        await callback.answer("Ошибка при обновлении заявки!", show_alert=True)
