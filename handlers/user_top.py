from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from function.user_req import UserFunction
user = Router()
from aiogram.types import FSInputFile

image_url = 'images/image_top.jpg'
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



    