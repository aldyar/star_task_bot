from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Filter
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from config import ADMIN
from function.mini_adds_req import MiniAdds as MiniAddsFunction
from app.states import MiniAdds as MiniAddsState
from aiogram.utils.text_decorations import html_decoration

admin = Router()

class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in ADMIN
    

@admin.callback_query(F.data =='MiniAdds')
async def mini_adds_handler(callback:CallbackQuery,state:FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer('*Выберите тип мини рекламы*',parse_mode='Markdown',reply_markup=kb.mini_adds_choose)


@admin.callback_query(F.data.startswith('choose_'))
async def choose_type_job(callback:CallbackQuery):
    await callback.message.delete()
    type = callback.data.removeprefix("choose_")
    keyboard = await kb.mini_adds_menu(type)
    await callback.message.answer('*Выберите действие:*',parse_mode='Markdown',reply_markup=keyboard)


@admin.callback_query(F.data.startswith('Mini_'))
async def to_mini_adds(callback:CallbackQuery):
    await callback.message.delete()
    type = callback.data.removeprefix("Mini_")
    mini_adds = await MiniAddsFunction.get_mini_add(type)
    if mini_adds:
        if type == 'start':
            add_name = 'Стартовая'
        else:
            add_name = 'Базовая'
        for mini_adds_list in mini_adds:
            text = f"""
<b>{add_name} мини реклама</b>

<b>Текст рекламы:</b>
{mini_adds_list.text}

<b>Текст кнопки:</b> 
{mini_adds_list.button_text}

<b>Ссылка кнопки:</b> 
{mini_adds_list.url}
"""
            keyboard = await kb.mini_adds_set(mini_adds_list.id)
            await callback.message.answer(text, parse_mode='HTML', reply_markup=keyboard)

    else:
        if type == 'start':
            text = '<b>У вас нет стартовой рекламы</b>'
        elif type == 'base':
            text = '<b>У вас нет базовой рекламы</b>'
        keyboard = await kb.add_mini_adds(type)
        await callback.message.answer(text, parse_mode='HTML', reply_markup=keyboard)

@admin.callback_query(F.data.startswith('CreateMiniAdds_'))
async def create_mini_adds(callback:CallbackQuery,state:FSMContext):
    await callback.message.delete()
    type = callback.data.removeprefix('CreateMiniAdds_')
    await state.update_data(type=type)
    await state.set_state(MiniAddsState.wait_text)
    await callback.message.answer('*Введите пожалуйста текст рекламы*',parse_mode='Markdown')

@admin.message(MiniAddsState.wait_text)
async def wait_text_add(message:Message,state:FSMContext):
    text = html_decoration.unparse(message.text, message.entities)
    #text = message.text
    await state.update_data(text = text)
    await state.set_state(MiniAddsState.wait_button_text)
    await message.answer('*Введите пожалуйста текст кнопки*',parse_mode='Markdown')

@admin.message(MiniAddsState.wait_button_text)
async def wait_text_button(message:Message,state:FSMContext):
    button_text = message.text
    await state.update_data(button_text = button_text)
    await state.set_state(MiniAddsState.wait_url)
    await message.answer('*Отправьте ссылку*',parse_mode='Markdown')

@admin.message(MiniAddsState.wait_url)
async def wait_url_button(message:Message,state:FSMContext):
    url = message.text
    data = await state.get_data()
    type = data.get('type') 
    add_text = data.get('text')
    button_text = data.get('button_text')
    await MiniAddsFunction.set_mini_add(type,add_text,button_text,url)
    await message.answer('*✅ Данные успешно сохранены*',parse_mode='Markdown')

    mini_adds = await MiniAddsFunction.get_mini_add(type)
    if type == 'start':
        add_name = 'Стартовая'
    else:
        add_name = 'Базовая'
    text=f"""
<b>{add_name} мини реклама</b>

<b>Текст рекламы:</b>
{add_text}

<b>Текст кнопки:</b> 
{button_text}

<b>Ссылка кнопки:</b> 
{url}
"""
    keyboard = await kb.mini_adds_set(type)
    await message.answer(text,parse_mode='HTML',reply_markup=keyboard)


@admin.callback_query(F.data.startswith('DeleteMini_'))
async def delet_mini_adds(callback:CallbackQuery,state:FSMContext):
    await callback.message.delete()
    type = callback.data.removeprefix("DeleteMini_")
    await MiniAddsFunction.delete_mini_adds(type)
    await callback.message.answer('*Мини реклама успешно была удалена*',parse_mode='Markdown')

