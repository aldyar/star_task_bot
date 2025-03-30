from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command, CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.states import EditRef
import re
from app.database.requests import (get_config, edit_ref_text, edit_ref_reward, edit_start_text,return_start_text, 
                                   set_image_url, delete_image_url,get_image_url)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN
from aiogram import Bot
import os
# Папка для хранения изображений
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)
from aiogram.types import FSInputFile


admin = Router()

class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in ADMIN
    

"""@admin.message(Admin(),F.text == 'Приветствие')
async def start_setting(message: Message,state:FSMContext):
    await message.answer('*Выберите что хотите поменять:*',parse_mode='Markdown')"""

from aiogram.fsm.state import StatesGroup, State

class AdminState(StatesGroup):
    waiting_for_text = State()
    waiting_for_image = State()

@admin.message(Admin(), F.text == 'Приветствие')
async def start_setting(message: Message, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить текст', callback_data='editstarttext')],
        [InlineKeyboardButton(text='Изменить картинку', callback_data='editimage')]
    ])
    await message.answer('*Выберите что хотите поменять:*', parse_mode='Markdown', reply_markup=keyboard)


@admin.callback_query(F.data == 'editstarttext')
async def edit_text(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Вернуть первый текст', callback_data='reset_text')]
    ])
    await state.set_state(AdminState.waiting_for_text)
    await callback.message.answer('Отправьте новый текст в формате Markdown', reply_markup=keyboard)
    await callback.message.delete()



@admin.callback_query(F.data == 'reset_text')
async def reset_text_handler(callback:CallbackQuery):
    await return_start_text()
    await callback.message.answer('*Первичный текст установлен*',parse_mode='Markdown')
    await callback.message.delete()



@admin.message(AdminState.waiting_for_text, F.text)
async def receive_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    print(message.text)
    await preview(message, state)


async def preview(message: Message, state: FSMContext):
    data = await state.get_data()
    text = data.get('text')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Сохранить', callback_data='save')],
        [InlineKeyboardButton(text='❌ Отменить', callback_data='cancel')]
    ])
    await message.answer(text, parse_mode='Markdown', reply_markup=keyboard)

@admin.callback_query(F.data == 'save')
async def save_changes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('text')
    await edit_start_text(text)
    await state.clear()
    await callback.message.delete()
    await callback.message.answer('Изменения сохранены ✅')

@admin.callback_query(F.data == 'cancel')
async def cancel_changes(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer('Изменения отменены ❌')






@admin.callback_query(F.data == 'editimage')
async def edit_image(callback: CallbackQuery, state: FSMContext):
    image_path = await get_image_url()  # Получаем путь к изображению
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Удалить картинку', callback_data='delete_image')],
        [InlineKeyboardButton(text = 'Изменить картинку',callback_data='processeditimage')]
    ])
    if image_path and os.path.exists(image_path):
        # Используем FSInputFile для загрузки фото
        photo = FSInputFile(image_path)
        await callback.message.answer_photo(photo, caption="*Ваша картинка*",parse_mode='Markdown', reply_markup=keyboard)
    else:
        # Если изображения нет, отправляем сообщение
        await callback.message.answer("У вас нет картинки.", reply_markup=keyboard)

    await callback.message.delete()


@admin.callback_query(F.data == 'processeditimage')
async def new_image_handler(callback:CallbackQuery,state:FSMContext):
    await callback.message.delete()
    await callback.message.answer('*Отправьте картину:*',parse_mode='Markdown')
    await state.set_state(AdminState.waiting_for_image)

@admin.message(AdminState.waiting_for_image, F.photo)
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
        local_filename = os.path.join(IMAGE_DIR, "image.jpg")
        print(f"Saving image to: {local_filename}")
        await bot.download_file(file_path, local_filename)
        print("Image successfully saved")
        
        # Сохранение в БД
        image_url = f"{local_filename}"  # Подставь свою логику URL
        print(f"Saving to DB: {image_url}")
        await set_image_url(image_url)  # Используем функцию сохранения ссылки
        print("Image URL saved to database")
        
        await state.clear()
        await message.answer("Изображение сохранено!")

    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer(f"Ошибка: {e}")



@admin.callback_query(F.data == 'delete_image')
async def delete_image(callback: CallbackQuery):
    image_path = await get_image_url()  # Получаем путь к файлу
    print(f"До нормализации: {image_path}")

    if image_path:
        image_path = os.path.normpath(image_path)
        print(f"После нормализации: {image_path}")

    if image_path and os.path.exists(image_path):
        os.remove(image_path)  # Удаляем файл
        await delete_image_url()  # Удаляем ссылку из БД
        await callback.message.answer("Изображение удалено!")
        await callback.message.delete()

    else:
        await callback.message.answer("У вас нет сохраненного изображения.")

    await callback.answer()


@admin.message(F.photo)
async def debug_photo(message: Message):
    print("Фото получено!")
    await message.answer("Фото обработано!")