from aiogram import Router, F
from aiogram.types import Message, CallbackQuery,InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp
from pprint import pprint
from database.requests import get_user
user = Router()
from config import FLYER, SUBGRAM_TOKEN
from app.storage import SubgramCaptcha
from function.subgram_req import SubGramFunction


from flyerapi import Flyer
flyer = Flyer(FLYER)

@user.callback_query(F.data.startswith('CheckFlyer_'))
async def check_flyer(callback: CallbackQuery,state:FSMContext):
    from handlers.user import withdraw,task_handler,get_task_hander,success_message
    await callback.message.delete()
    mark = callback.data.split("CheckFlyer_")[1]
    print(f"Получен mark: {mark}")
    if not await flyer.check(callback.from_user.id,callback.from_user.language_code):
        keyboard = await kb.check_flyer(mark)
        await callback.message.answer('⬇️*После выполнения условий нажмите на кнопку ниже*',parse_mode='Markdown', reply_markup=keyboard)
        return
    print(f"YAA TUTAAA")
    if mark == 'withdraw':
        await withdraw(callback)
    elif mark == 'start':
        await success_message(callback,state)
    elif mark == 'TaskInline':
        await task_handler(callback,state)
    elif mark == 'Task':
        await get_task_hander(callback,state)


# async def subgram_captcha(message: Message|CallbackQuery):
#     pass


# async def send_post(user_id: int, name: str, premium: bool, gender: str) -> dict:
#     url = "https://api.subgram.ru/request-op/"
#     headers = {
#         "Auth": SUBGRAM_TOKEN
#     }
#     data = {
#         "UserId": user_id,
#         "ChatId": user_id,
#         "Gender": gender,
#         "first_name": name,
#         "language_code": "ru",
#         "Premium": premium,
#         "actions": "newtask"
#     }

#     async with aiohttp.ClientSession() as session:
#         resp = await session.post(url, json=data, headers=headers)
#         pprint(await resp.text())
#         return await resp.json()


# async def get_unsubscribed_channel_links(response: dict):
#     unsubscribed_links = []
#     sponsors = response.get("additional", {}).get("sponsors", [])

#     for sponsor in sponsors:
#         if sponsor.get("status") == "unsubscribed":
#             unsubscribed_links.append({
#                 "link": sponsor.get("link"),
#                 "type": sponsor.get("type"),
#                 "name": sponsor.get("resource_name") or "Подписаться",
#                 "complete": False
#             })

#     return unsubscribed_links



@user.message(F.text == 'subtest')
async def subgram_captcha(message: Message|CallbackQuery,type):
    reply_target = message.message if isinstance(message, CallbackQuery) else message
    user = message.from_user
    print(f'USER___________{user.id}')
    gender = await get_user(user.id)
    response = await SubGramFunction.send_post(
        user_id=user.id,
        name=user.first_name or "Пользователь",
        premium=user.is_premium,
        gender=gender.gender or "male"
    )

    unsubscribed = await SubGramFunction.get_unsubscribed_channel_links(response)

    if not unsubscribed:
        #await message.answer("Ты подписан на все нужные ресурсы ✅")
        return True

    SubgramCaptcha[user.id] = [item['link'] for item in unsubscribed]
    # Создаём клавиатуру
    kb = InlineKeyboardBuilder()

     # Добавляем кнопки подписки по 2 в ряд
    row = []
    for i, item in enumerate(unsubscribed, 1):
        text = "🤖 Запустить бота" if item['type'] == 'bot' else "📢 Подписаться"
        row.append(InlineKeyboardButton(text=text, url=item["link"]))
        if i % 2 == 0:
            kb.row(*row)
            row = []
    if row:  # если осталась одна кнопка
        kb.row(*row)

    # Добавляем кнопку "Проверить" отдельно внизу
    kb.row(
        InlineKeyboardButton(
            text="🔄 Проверить",
            callback_data=f"SubgramCaptcha_{type}"
        )
    )

    await reply_target.answer(
        "<b>Чтобы получить доступ к функциям бота, необходимо подписаться на ресурсы.</b> 🌟\n\n" \
        "<span class=\"tg-spoiler\">не отписывайтесь от каналов в течении как минимум 24 часов. Иначе нам придется наложить санкции</span> ",
        parse_mode='HTML',
        reply_markup=kb.as_markup()
    )


@user.callback_query(F.data.startswith ('SubgramCaptcha_'))
async def check_subgram_capthca(callback: CallbackQuery,state:FSMContext):
    from handlers.user_profile import user_profile_handler
    from handlers.user_top import top_handler
    from handlers.user import bonus, withdraw
    type = callback.data.removeprefix('SubgramCaptcha_')
    user_id = callback.from_user.id

    # Получаем ссылки из SubgramCaptcha
    links = SubgramCaptcha.get(user_id)
    print(f"[DEBUG] SubgramCaptcha[{user_id}] = {links}")
    if not links:
        await callback.answer("Нет ссылок для проверки. Попробуй сначала.", show_alert=True)
        return

    # Проверяем подписку
    is_subscribed = await SubGramFunction.check_captcha(user_id, links)

    if is_subscribed:
        if type == 'profile':
            await user_profile_handler(callback,state)
        elif type == 'top':
            await top_handler(callback,state)
        elif type == 'bonus':
            await bonus(callback)
        elif type == 'withdraw':
            await withdraw(callback)
        await callback.message.delete()
    else:
        await callback.answer("❌ Ты ещё не подписан на все ресурсы.")
        await callback.message.delete()
        await subgram_captcha(callback,type)







# @user.message(F.text == 'subtest')
# async def subgram_captcha(message: Message,type):
#     user = message.from_user
#     print(f'USER___________{user.id}')
#     gender = await get_user(user.id)
#     response = await SubGramFunction.send_post(
#         user_id=user.id,
#         name=user.first_name or "Пользователь",
#         premium=user.is_premium,
#         gender=gender.gender or "male"
#     )

#     unsubscribed = await SubGramFunction.get_unsubscribed_channel_links(response)

#     if not unsubscribed:
#         #await message.answer("Ты подписан на все нужные ресурсы ✅")
#         return True

#     SubgramCaptcha[user.id] = [item['link'] for item in unsubscribed]
#     # Создаём клавиатуру
#     kb = InlineKeyboardBuilder()

#     for item in unsubscribed:
#         if item['type'] == 'bot':
#             kb.button(text="🤖 Запустить бота", url=item["link"])
#         else:
#             kb.button(text="📢 Подписаться", url=item["link"])

#     # Кнопка "Проверить"
#     kb.button(text="🔄 Проверить", callback_data=f"SubgramCaptcha_{type}")

#     kb.adjust(2)

#     await message.answer(
#         "<b>Чтобы получить доступ к функциям бота, необходимо подписаться на ресурсы.</b> 🌟\n\n" \
#         "<span class=\"tg-spoiler\">не отписывайтесь от каналов в течении как минимум 24 часов. Иначе нам придется наложить санкции</span> ",
#         parse_mode='HTML',
#         reply_markup=kb.as_markup()
#     )