from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command
from aiogram.fsm.context import FSMContext

admin = Router()


class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in [1075213318]
    

@admin.message(Admin(), Command('newsletter'))
async def newsletter(message: Message, state: FSMContext):
    await state.set_state(Newsletter.message)
    await message.answer('Введите сообщение рассылки')
