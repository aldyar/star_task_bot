from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command, CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.states import Reminder as ReminderState
import re
from app.database.requests import (get_config, edit_ref_text, edit_ref_reward, edit_start_text,return_start_text, 
                                   set_image_url, delete_image_url,get_image_url)
from app.database.reminder_req import ReminderFunction as Reminder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN
import os
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)
from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.utils.text_decorations import html_decoration


admin = Router()

class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in ADMIN
    

@admin.message(Admin(), F.text == 'Напоминание')
async def reminder_handler(message:Message):
    await message.answer('*Выберите что хотите поменять:*',parse_mode='Markdown',reply_markup=kb.inline_admin_reminder)


@admin.callback_query(F.data == 'ResetTextReminder')
async def reset_reminder_text_handler(callback:CallbackQuery):
    text = await Reminder.get_config_reminder_text()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить', callback_data='EditReminderText')]])
    if text:
        await callback.message.answer('Ваш текст:\n\n'
                                      f'{text}',parse_mode='HTML',reply_markup=keyboard)
    else:
        await callback.message.answer('Ваш текст:\n\n'
                                      f'У вас нет текста',parse_mode='HTML',reply_markup=keyboard)
    await callback.message.delete()
        

@admin.callback_query(F.data == 'EditReminderText')
async def edit_reminder_text_handler(callback:CallbackQuery,state:FSMContext):
    await callback.message.answer('Введите текст:')
    await state.set_state(ReminderState.wait_text)
    await callback.message.delete()


@admin.message(ReminderState.wait_text)
async def wait_text_handler(message:Message,state:FSMContext):
    text_with_html = html_decoration.unparse(message.text, message.entities)
    await state.update_data(text=text_with_html)
    await preview(message, state)


async def preview(message: Message, state: FSMContext):
    data = await state.get_data()
    text = data.get('text')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Сохранить', callback_data='SaveReminderText')],
        [InlineKeyboardButton(text='❌ Отменить', callback_data='CancelReminderText')]
    ])
    await message.answer(text,parse_mode='HTML',  reply_markup=keyboard)


@admin.callback_query(F.data == 'SaveReminderText')
async def save_changes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('text')
    await Reminder.set_reminder_text(text)
    await state.clear()
    await callback.message.delete()
    await callback.message.answer('Изменения сохранены ✅')


@admin.callback_query(F.data == 'CancelReminderText')
async def cancel_changes(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer('Изменения отменены ❌')


@admin.callback_query(F.data == 'ResetImageReminder')
async def reset_image_reminder_handler(callback:CallbackQuery):
    image_path = await Reminder.get_config_reminder_image()  # Получаем путь к изображению
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Удалить картинку', callback_data='DeleteImageReminder')],
        [InlineKeyboardButton(text = 'Изменить картинку',callback_data='EditImageReminder')]
    ])
    if image_path and os.path.exists(image_path):
        # Используем FSInputFile для загрузки фото
        photo = FSInputFile(image_path)
        await callback.message.answer_photo(photo, caption="*Ваша картинка*",parse_mode='Markdown', reply_markup=keyboard)
    else:
        # Если изображения нет, отправляем сообщение
        await callback.message.answer("У вас нет картинки.", reply_markup=keyboard)

    await callback.message.delete()


@admin.callback_query(F.data == 'EditImageReminder')
async def new_image_handler(callback:CallbackQuery,state:FSMContext):
    await callback.message.delete()
    await callback.message.answer('*Отправьте картину:*',parse_mode='Markdown')
    await state.set_state(ReminderState.wait_image)


@admin.message(ReminderState.wait_image, F.photo)
async def receive_image(message: Message, state: FSMContext, bot: Bot):
    try:
        print("Получено фото от пользователя")
        photo = message.photo[-1]
        print(f"Photo ID: {photo.file_id}")
        
        file_info = await bot.get_file(photo.file_id)
        print(f"File info: {file_info}")
        file_path = file_info.file_path
        print(f"File path: {file_path}")

        # Сохранение фото
        local_filename = os.path.join(IMAGE_DIR, "image_reminder.jpg")
        print(f"Saving image to: {local_filename}")
        await bot.download_file(file_path, local_filename)
        print("Image successfully saved")
        
        # Сохранение в БД
        image_url = f"{local_filename}"  # Подставь свою логику URL
        print(f"Saving to DB: {image_url}")
        await Reminder.set_reminder_image(image_url)  # Используем функцию сохранения ссылки
        print("Image URL saved to database")
        
        await state.clear()
        await message.answer("Изображение сохранено!")

    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer(f"Ошибка: {e}")



@admin.callback_query(F.data == 'DeleteImageReminder')
async def delete_image(callback: CallbackQuery):
    image_path = await Reminder.get_config_reminder_image()  # Получаем путь к файлу
    print(f"До нормализации: {image_path}")

    if image_path:
        image_path = os.path.normpath(image_path)
        print(f"После нормализации: {image_path}")

    if image_path and os.path.exists(image_path):
        os.remove(image_path)  # Удаляем файл
        await Reminder.delete_image()  # Удаляем ссылку из БД
        await callback.message.answer("Изображение удалено!")
        await callback.message.delete()

    else:
        await callback.message.answer("У вас нет сохраненного изображения.")

    await callback.answer()