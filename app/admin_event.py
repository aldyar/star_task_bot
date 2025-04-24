from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command, CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.states import Event
import re
from app.database.requests import (get_config, edit_ref_text, edit_ref_reward, edit_start_text,return_start_text, 
                                   set_image_url, delete_image_url,get_image_url)
from app.database.reminder_req import ReminderFunction as Reminder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN
import os
from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.utils.text_decorations import html_decoration
from app.database.user_req import UserFunction as User
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError
import asyncio
import text as txt
IMAGE_DIR = "images"
from datetime import datetime
from app.database.event_req import EventFunction 
from config import CHANNEL_ID


admin = Router()

class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in ADMIN
    

@admin.message(Admin(),F.text == 'Конкурс')
async def even_handler(message:Message):
    await message.answer('Ваш конкурс',reply_markup=kb.inline_admin_event)


@admin.callback_query(F.data == 'ActiveEvent')
async def get_active_event(callback:CallbackQuery):
    event = await EventFunction.get_active_event()
    if event:
        photo = FSInputFile(event.image)
        button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Отправить конкурс',callback_data='SendEvent')],
                                                       [InlineKeyboardButton(text = 'Удалить конкурс',callback_data=f'DeleteEvent_{event.id}')]])
        await callback.message.answer_photo(photo,caption=event.text,reply_markup=button)
        print(f'EVENT ID ===== {event.id}')
        await callback.answer()
    await callback.answer('На данный момент нет активного конкурса')


@admin.callback_query(F.data == 'CreateEvent')
async def create_event_handler(callback:CallbackQuery):
    event = await EventFunction.check_active_event()
    if event:
        return await callback.answer('У вас уже есть активный конкурс')
    await callback.message.answer(txt.create_event,reply_markup=kb.inline_type_event)
    await callback.answer()


@admin.callback_query(F.data.startswith('Event_'))
async def type_event_handler(callback:CallbackQuery,state:FSMContext):
    type = callback.data.removeprefix("Event_")
    await state.update_data(type=type)

    type4_text = 'Введите колличество звезд которое получат участники конкурса...'
    text = 'Введите колличество звезд которое получит пользователь за 1 место'

    if type == '4':
        await callback.message.answer(type4_text)
    else: 
        await callback.message.answer(text)

    await state.set_state(Event.wait_c1)
    await callback.answer()


@admin.message(Event.wait_c1)
async def wait_c1_handler(message:Message,state:FSMContext):
    c1 = message.text
    await state.update_data(c1=c1)
    data = await state.get_data()
    type = data.get("type")

    type4_text = 'Введите колличество призовых мест'
    text = 'Введите колличество звезд которое получит пользователь за 2 место'

    if type == '4':
        await message.answer(type4_text)
    else: 
        await message.answer(text)

    await state.set_state(Event.wait_c2)


@admin.message(Event.wait_c2)
async def wait_c2_handler(message:Message,state:FSMContext):
    c2 = message.text
    await state.update_data(c2=c2)
    data = await state.get_data()
    type = data.get("type")

    type4_text = 'Введите колличество пользователей которое должен привести для участия в конкурсе'
    text = 'Введите колличество звезд которое получит пользователь за 3 место'

    if type == '4':
        await message.answer(type4_text)
        await state.set_state(Event.wait_rule)
    else: 
        await message.answer(text)
        await state.set_state(Event.wait_c3)


@admin.message(Event.wait_c3)
async def wait_c3_handler(message:Message,state:FSMContext):
    c3 = message.text
    await state.update_data(c3=c3)
    data = await state.get_data()
    type = data.get("type")

    type1_text = 'Введите колличество звезд которые получат пользователи за 4-20 место'
    type2_text = 'Введите колличество звезд которые получат пользователи за 4-40 место'
    type3_text = 'Введите колличество звезд которые получат пользователи за 4-100 место'

    if type == '1':
        await message.answer(type1_text)
    elif type == '2': 
        await message.answer(type2_text)
    elif type == '3':
        await message.answer(type3_text)
    
    await state.set_state(Event.wait_c4)


@admin.message(Event.wait_c4)
async def wait_c4_handler(message:Message,state:FSMContext):
    c4 = message.text
    await state.update_data(c4=c4)
    data = await state.get_data()
    type = data.get("type")

    type1_text = 'Введите колличество звезд которые получат пользователи за 21-50 место'
    type2_text = 'Введите колличество звезд которые получат пользователи за 41-100 место'
    type3_text = 'Введите колличество звезд которые получат пользователи за 101-300 место'

    if type == '1':
        await message.answer(type1_text)
    elif type == '2': 
        await message.answer(type2_text)
    elif type == '3':
        await message.answer(type3_text)
    
    await state.set_state(Event.wait_c5)


@admin.message(Event.wait_c5)
async def wait_c5_handler(message:Message,state:FSMContext):
    c5 = message.text
    await state.update_data(c5=c5)
    data = await state.get_data()
    type = data.get("type")

    type1_text = 'Введите колличество звезд которые получат пользователи за 51-100 место'
    type2_text = 'Введите колличество звезд которые получат пользователи за 101-200 место'
    type3_text = 'Введите колличество звезд которые получат пользователи за 301-500 место'

    if type == '1':
        await message.answer(type1_text)
    elif type == '2': 
        await message.answer(type2_text)
    elif type == '3':
        await message.answer(type3_text)
    
    await state.set_state(Event.wait_c6)


@admin.message(Event.wait_c6)
async def wait_c5_handler(message:Message,state:FSMContext):
    c6 = message.text
    await state.update_data(c6=c6)
    data = await state.get_data()
    type = data.get("type")

    text = 'Введите колличество пользователей которое должен привести для участия в конкурсе'

    await message.answer(text)
    await state.set_state(Event.wait_rule)

@admin.message(Event.wait_rule)
async def wait_rule_handler(message:Message,state:FSMContext):
    rule = message.text
    await state.update_data(rule = rule)
    data = await state.get_data()
    type = data.get("type")

    text = 'Введите текст конкурса...'
    await message.answer(text)
    await state.set_state(Event.wait_text)


@admin.message(Event.wait_text)
async def wait_text_handler(message:Message,state:FSMContext):
    text = message.text
    await state.update_data(text = text)
    data = await state.get_data()
    type = data.get("type")

    text = 'Отправьте картинку...'
    await message.answer(text)
    await state.set_state(Event.wait_image)


@admin.message(Event.wait_image, F.photo)
async def wait_image_handler(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        file_path = file_info.file_path
        # Сохранение фото
        local_filename = os.path.join(IMAGE_DIR, "image_event.jpg")
        await bot.download_file(file_path, local_filename)

        # Сохранение в БД
        image_url = f"{local_filename}"  # Подставь свою логику URL

        await state.update_data(image = image_url)  # Используем функцию сохранения ссылки

        
    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer(f"Ошибка: {e}")
    today_date = datetime.now().strftime('%d-%m-%Y')
    text = (
        "📅 Пожалуйста, введите дату окончания конкурса в формате: *дд-мм-гггг*\n"
        f"📌 Пример сегодняшней даты: `{today_date}`"
    )
    await message.answer(text ,parse_mode='Markdown')
    await state.set_state(Event.end_date)


@admin.message(Event.end_date)
async def wait_text_handler(message:Message,state:FSMContext):
    date = message.text.strip()
    await state.update_data(end_date = date)
    await preview(message,state)
    # data = await state.get_data()
    # type = data.get("type")
    # c1 = data.get("c1")
    # c2 = data.get("c2")
    # rule = data.get("rule")
    # text = data.get("text")
    # image = data.get("image")
    # end_date = datetime.strptime(date, "%d-%m-%Y")
    # if type == '4':
    #     await EventFunction.create_event(c1,c2,type,rule,text,image,end_date)
    # else:
    #     c3 = data.get("c3")
    #     c4 = data.get("c4")
    #     c5 = data.get("c5")
    #     c6 = data.get("c6")
    #     await EventFunction.create_event(c1,c2,c3,c4,c5,c6,type,rule,text,image,end_date)
    # await message.answer('Готово создано')
    # await state.clear()

async def preview(message:Message,state:FSMContext):
    data = await state.get_data()
    text = data.get("text")
    image = data.get("image")
    photo = FSInputFile(image)
    await message.answer_photo(photo,caption=text,reply_markup=kb.inline_save_or_delete_event)

@admin.callback_query(F.data == 'EventSave')
async def save_event(callback:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    type = data.get("type")
    c1 = data.get("c1")
    c2 = data.get("c2")
    rule = data.get("rule")
    text = data.get("text")
    image = data.get("image")
    date = data.get("end_date")
    end_date = datetime.strptime(date, "%d-%m-%Y")
    if type == '4':
        await EventFunction.create_event(c1,c2,None,None,None,None,type,rule,text,image,end_date)
    else:
        c3 = data.get("c3")
        c4 = data.get("c4")
        c5 = data.get("c5")
        c6 = data.get("c6")
        await EventFunction.create_event(c1,c2,c3,c4,c5,c6,type,rule,text,image,end_date)
    await callback.message.answer('Конкурс сохранен')
    await callback.message.delete()
    await state.clear()


@admin.callback_query(F.data == 'EventDontSave')
async def dont_save_event(callback:CallbackQuery,state:FSMContext):
    await callback.message.answer('Конкурс не сохранен')
    await state.clear()


@admin.callback_query(F.data == 'SendEvent')
async def send_event_handler(callback:CallbackQuery,bot:Bot):
    users = await User.get_all_users()
    user_ids = [user.tg_id for user in users]
    event = await EventFunction.get_active_event()
    photo = FSInputFile(event.image)
    keyboard = await kb.inline_join_event(event.id)
    message = await bot.send_photo(
                    CHANNEL_ID,
                    photo=photo,
                    caption=event.text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
    await EventFunction.save_message_id(message.message_id)
    for user_id in user_ids:
        try:
            await bot.send_photo(
                    user_id,
                    photo=photo,
                    caption=event.text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
        except TelegramAPIError as e:  # Любая другая ошибка
            print(f"Ошибка отправки {user_id}: {e}")
        await asyncio.sleep(0.3)  # Задержка, чтобы избежать блокировки
    

@admin.callback_query(F.data.startswith('eventjoin_'))
async def join_event_handler(callback:CallbackQuery,bot:Bot):
    event_id = callback.data.removeprefix("eventjoin_")

    event = await EventFunction.get_active_event()
    if await EventFunction.check_active_event_by_id(event_id) == False:
        return await callback.answer('Конкурс завершен',show_alert=True)
    if await EventFunction.check_user_referrals_in_event(callback.from_user.id) == 0:
        return await callback.answer('Вы не выполнили условия',show_alert=True)
    await EventFunction.add_participant_to_event(callback.from_user.id,bot)
    await callback.answer('Вы участвуете в конкурсе',show_alert=True)


@admin.callback_query(F.data.startswith('DeleteEvent_'))
async def delete_event_handler(callback:CallbackQuery):
    event_id = callback.data.removeprefix("DeleteEvent_")
    print(f'EVENT_ID ===== {event_id}')
    await EventFunction.delete_event(event_id)
    await callback.answer('Конкурс удален')
    await callback.message.delete()