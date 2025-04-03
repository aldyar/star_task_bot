from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command, CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.states import CreateTask, EditTask
import re
from app.database.requests import get_all_tasks, get_task, edit_task_reward, edit_task_active, edit_task_total_completion, create_task,get_task_about_taskid
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton
from app.database.models import User, Config, Task, TaskCompletion
from app.database.models import async_session
from config import ADMIN
from aiogram.utils.text_decorations import html_decoration

admin = Router()


class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in ADMIN
    

@admin.message(Admin(), CommandStart())
async def start_admin(message: Message,state:FSMContext):
    await state.clear()
    await message.answer('Добро пожаловать в панель Администратора.',reply_markup = kb.main_admin)


@admin.message(Admin(),F.text == 'Задание')
async def tasks (message: Message,state:FSMContext):
    await state.clear()
    text = """
📋 *Панель Администратора* 
Добро пожаловать! Здесь вы можете управлять заданиями.  

✨ *Создавать новые задания* или 🔄 *Редактировать существующие* — всё в ваших руках!  

Что хотите сделать? ⬇️
"""
    await message.answer(text, parse_mode='Markdown', reply_markup=kb.tasks_menu)


@admin.callback_query(F.data == 'create_task')
async def create_task_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('📌Выберите тип задания ',reply_markup=kb.inline_task_type)
    await callback.answer()

@admin.callback_query(F.data.in_({'subscribe', 'entry'}))
async def task_type_process(callback: CallbackQuery, state: FSMContext):
    task_type = callback.data 
    await state.update_data(task_type=task_type)
    await callback.message.answer(
        "📌 Введите ссылку на задание в формате `https://t.me/...`", parse_mode='Markdown', disable_web_page_preview=True
    )
    await state.set_state(CreateTask.waiting_for_link)
    await callback.answer()

@admin.message(CreateTask.waiting_for_link)
async def process_link(message: Message, state: FSMContext):
    link = message.text.strip()
    await state.update_data(link=link)
    await message.answer('Введите описание задания разметкой Markdown...',reply_markup=kb.describe_inline)
    await state.set_state(CreateTask.waiting_for_description)


@admin.message(CreateTask.waiting_for_description)
async def process_describe(message:Message,state:FSMContext):
    describe = html_decoration.unparse(message.text, message.entities)
    await state.update_data(describe = describe)
    await message.answer("💰 Введите вознаграждение за выполнение (в цифрах):")
    await state.set_state(CreateTask.waiting_for_reward)



@admin.callback_query(F.data == 'describe_none')
async def describe_none_handler(callback:CallbackQuery,state:FSMContext):
    await callback.message.delete()
    await callback.message.answer("💰 Введите вознаграждение за выполнение (в цифрах):")
    await state.set_state(CreateTask.waiting_for_reward)



@admin.message(CreateTask.waiting_for_reward)
async def process_reward(message: Message, state: FSMContext):
    try:
        reward = float(message.text)  # Принимает любые числа: целые и дробные
    except ValueError:
        await message.answer("❌ Пожалуйста, введите вознаграждение числом.")
        return

    await state.update_data(reward=reward)
    await message.answer("📊 Введите количество выполнений (в цифрах):")
    await state.set_state(CreateTask.waiting_for_count)



@admin.message(CreateTask.waiting_for_count)
async def process_count(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Пожалуйста, введите количество выполнений числом.")
        return
    
    await state.update_data(count=int(message.text))
    await message.answer('📨 Перешлите любое сообщение из данной канала:')
    await state.set_state(CreateTask.waiting_fot_chat_id)
    

@admin.message(CreateTask.waiting_fot_chat_id)
async def process_chat_id(message: Message, state: FSMContext):
    if message.forward_from_chat:  # Проверяем, что сообщение переслано из чата или канала
        chat_id = message.forward_from_chat.id
        title =  message.forward_from_chat.title
        await message.answer(f"Chat ID успешно получен: `{chat_id}`", parse_mode="Markdown")
        data = await state.get_data()
        link = data['link'] 
        reward = data['reward']
        count = data['count']
        task_type = data['task_type']
        describe = data.get('describe')
        print(f'link: {link}, reward: {reward}, count: {count}')
        await create_task(link, reward, count, chat_id,title, task_type, describe)

        text = f"""
    ✅ <b>Задание успешно создано!</b>
    📌 <b>Ссылка:</b> <a href="{link}">{link}</a>
    💰 <b>Вознаграждение:</b> {reward}
    📊 <b>Количество выполнений:</b> {count}
    ✉️ <b>ID канала:</b> {chat_id}
"""

        if describe:
            await message.answer(f"\n📝 Описание: {describe}", parse_mode='HTML')
        await message.answer(text, parse_mode='HTML', disable_web_page_preview=True)
        await state.clear()
        
    else:
        await message.answer("Пожалуйста, перешли сообщение из канала.")



@admin.callback_query(F.data == 'edit_task')
async def show_tasks(callback: CallbackQuery):
    tasks = await get_all_tasks()  # Получаем все задачи из базы
    if not tasks:
        await callback.message.answer("❌ Нет созданных заданий.")
        await callback.answer()
        return

    for task in tasks:
        text = f"🔢 <b>Задание №{task.id}</b>\n\n"
        if task.description:
            text +=f"📋 <b>Описание:</b> {task.description}\n"
        text +=f'📌 <b>Ссылка:</b> <a href="{task.link}">{task.link}</a>\n'
        text +=f'💰 <b>Вознаграждение:</b> {task.reward}⭐\n'
        text +=f'📊 <b>Лимит выполнений:</b> {task.total_completions}\n'
        text +=f'✅ <b>Выполнено:</b> {task.completed_count}'

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='✏️ Редактировать', callback_data=f'editindividualtask_{task.id}')]
            ]
        )
        await callback.message.answer(text, parse_mode='HTML', reply_markup=keyboard, disable_web_page_preview=True)
    await callback.answer()



@admin.callback_query(F.data.startswith('editindividualtask_'))
async def edit_task(callback:CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split('_')[1])
    task = await get_task_about_taskid(task_id)

    if not task:
        await callback.message.answer("❌ Задание не найдено.")
        await callback.answer()
        return

    await state.update_data(task_id=task_id)

    text = f"""
📌 **Ссылка:** [{task.link}]({task.link})
💰 **Вознаграждение:** {task.reward}
📊 **Лимит выполнений:** {task.total_completions}
✅ **Выполнено:** {task.completed_count}
"""

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='💰 Изменить вознаграждение', callback_data=f'change_reward_{task_id}')],
            [InlineKeyboardButton(text='➕ Добавить выполнений', callback_data=f'add_completions_{task_id}')],
            [InlineKeyboardButton(text='🚫 Деактивировать задание', callback_data=f'deactivate_{task_id}')]
        ]
    )

    await callback.message.answer(text, parse_mode='Markdown', reply_markup=keyboard, disable_web_page_preview=True)
    await callback.answer()


@admin.callback_query(F.data.startswith('change_reward_'))
async def change_reward(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split('_')[-1])
    await state.update_data(task_id=task_id)
    await callback.message.answer("💰 Введите новое вознаграждение (числом):")
    await state.set_state(EditTask.changing_reward)
    await callback.answer()


@admin.message(EditTask.changing_reward)
async def process_change_reward(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите числовое значение.")
        return

    data = await state.get_data()
    task_id = data['task_id']
    task = await get_task_about_taskid(task_id)

    if task:
        await edit_task_reward(task_id, int(message.text))
        await message.answer("✅ Вознаграждение успешно изменено.")
    else:
        await message.answer("❌ Задание не найдено.")

    await state.clear()


@admin.callback_query(F.data.startswith('add_completions_'))
async def add_completions(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split('_')[-1])
    await state.update_data(task_id=task_id)
    await callback.message.answer("📊 Введите количество добавляемых выполнений:")
    await state.set_state(EditTask.adding_completions)
    await callback.answer()


@admin.message(EditTask.adding_completions)
async def process_add_completions(message: Message, state: FSMContext, ):
    if not message.text.isdigit():
        await message.answer("❌ Введите числовое значение.")
        return

    data = await state.get_data()
    task_id = data['task_id']
    task = await get_task_about_taskid(task_id)

    if task:
        await edit_task_total_completion(task_id, int(message.text))
        await message.answer("✅ Количество выполнений успешно добавлено.")
    else:
        await message.answer("❌ Задание не найдено.")

    await state.clear()


@admin.callback_query(F.data.startswith('deactivate_'))
async def deactivate_task(callback: CallbackQuery):
    task_id = int(callback.data.split('_')[-1])
    task = await get_task_about_taskid(task_id)

    if task:
        await edit_task_active(task_id)
        await callback.message.answer("🚫 Задание успешно деактивировано.")
    else:
        await callback.message.answer("❌ Задание не найдено.")

    await callback.answer()
