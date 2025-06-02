from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from handlers.user import withdraw,task_handler,get_task_hander

user = Router()
from config import ADMIN, GROUP_ID,CHANNEL_ID,FLYER


from flyerapi import Flyer
flyer = Flyer(FLYER)

@user.callback_query(F.data.startswith('CheckFlyer_'))
async def check_flyer(callback: CallbackQuery,state:FSMContext):
    await callback.answer()
    mark = callback.data.split("CheckFlyer_")[1]
    print(f"Получен mark: {mark}")
    if not await flyer.check(callback.from_user.id,callback.from_user.language_code):
        return
    if mark == 'withdraw':
        await withdraw(callback)
    elif mark == 'TaskInline':
        await task_handler(callback,state)
    elif mark == 'Task':
        await get_task_hander(callback,state)