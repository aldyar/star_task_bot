from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from database.requests import (set_user, get_config, get_bonus_update, update_bonus, check_tasks, get_user, 
                                   get_withdraw_limit, set_referrer_id, create_transaction, get_task,
                                   is_user_subscribed,completed_task,create_task_completions_history,check_subscriptions,
                                   check_user,insert_message_id, count_reward,join_request,skip_task,get_task_about_taskid)
from function.task_req import get_first_available_task,skip_task_function,create_task_state,get_task_state,create_task_history,check_entry_task_history
from app.keyboards import withdraw_inline, withdraw_keyboard
from aiogram.enums import ChatAction
from aiogram import Bot
import random
from datetime import datetime, timedelta
import text as txt

user = Router()

from config import ADMIN, GROUP_ID,CHANNEL_ID
from handlers.admin import start_admin
from aiogram import types
from aiogram.types import FSInputFile
import asyncio
from function.channel_req import StartChannelFunction as Channel
from function.subgram_req import SubGramFunction as Subgram
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton
from app.storage import SubgramList
from app.storage import BotEntry



@user.message(F.text == 'subgram')
async def test_subgram(message:Message,state:FSMContext,id):
    await state.clear()
    print(f"[TEST_HANDLER ]USERID   :_____ {message.from_user.id}")
    all_links = SubgramList.get(id, [])
    print(f"[DEBUG] SubgramList полностью: {SubgramList}")
    links = [item for item in all_links if not item.get("complete", False)]
    print(f'LINKS:______{links}')
    index = 0
    await state.update_data(index=index)
    if not links:
        return await get_task_hander(message,state,id)

    link = links[index]["link"]
    type = links[index]["type"]
    complete = SubgramList[id][index]["complete"]
    reward = 0.25
    text = f"🎯 <b>Доступно задание !</b>\n\n"
    keyboard = await kb.inline_subgram(link)
    if type == 'channel':
        text += f"• <b>Подпишись на</b> <a href='{link}'>{link}</a>\n"
    elif type =='bot':
        text += f"• <b>Запустите бота</b> <a href='{link}'>{link}</a>\n"
    else:
        text += f"• <b>Подпишись на</b> <a href='{link}'>{link}</a>\n"
    text += f"• <b>Награда:</b> {reward}⭐"
    #await state.update_data(task = task)
    #reward = await count_reward(message.from_user.id)
    # await message.answer_photo(photo,caption=f'*👑 Выполни все задания и получи* *{reward}⭐️!*\n\n'
    #                         '*🔻 Выполни текущее задание, чтобы открыть новое:*', parse_mode='Markdown')
    #keyboard = await kb.complete_task_inline(task.link)
    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True,reply_markup= keyboard)


@user.callback_query(F.data.startswith('SubComplete_'))
async def complete_subgram_task_handler(callback:CallbackQuery,state:FSMContext):
    link = callback.data.removeprefix("SubComplete_")
    user_id = callback.from_user.id
    check = await Subgram.check_subscribe(link,user_id)
    links = SubgramList.get(user_id, [])
    print(f"[DEBUG] SubgramList полностью: {SubgramList}")
    if check == 'subscribed':
        for item in links:
            if item.get("link") == link and not item.get("complete", False):
                item["complete"] = True
                await Subgram.add_reward_user_subgram(user_id,0.25)
                await callback.answer('⭐ Вознаграждение зачислено')
                await skip_subgram_task(callback,state)
                break
        else: # Только если ни один item не подошёл (break не сработал)
            #SubgramList[user_id] = []
            await callback.answer('Задание уже выполнено или не найдено', show_alert=True)
    elif check == 'notgetted':
        for item in links:
            if item.get("link") == link:
                item["complete"] = True
                await skip_subgram_task(callback,state)
                break
        await callback.answer('Задание уже выполнено или не найдено', show_alert=True)
    else:
        await callback.answer('Вы не выполнили условия',show_alert=True)


@user.callback_query(F.data == 'SkipSubgram')
async def skip_subgram_task(callback:CallbackQuery,state:FSMContext):
    #await callback.message.answer('затронул skip_subgram_task')
    print(f"[SKIP_TASK_HANDLER ]USERID   :_____ {callback.from_user.id}")
    print(f"[DEBUG] SubgramList полностью: {SubgramList}")
    #from handlers.user import get_task_hander
    await callback.message.delete()
    all_links = SubgramList.get(callback.from_user.id, [])
    links = [item for item in all_links if not item.get("complete", False)]
    data = await state.get_data()
    index = data.get('index')
    print(f'INDEX__________{index}')
    index += 1
    print(f'INDEX__________ AFTER{index}')
    if index >= len(links):
        await get_task_hander(callback.message,state,callback.from_user.id)
        return  #await callback.message.answer('pass',show_alert=True)
    link = links[index]["link"]
    print(f'LINK____________________{link}')
    type = links[index]["type"]
    complete = SubgramList[callback.from_user.id][index]["complete"]
    reward = 0.25
    text = f"🎯 <b>Доступно задание !</b>\n\n"
    keyboard = await kb.inline_subgram(link)
    if type == 'channel':
        text += f"• <b>Подпишись на</b> <a href='{link}'>{link}</a>\n"
    elif type =='bot':
        text += f"• <b>Запустите бота</b> <a href='{link}'>{link}</a>\n"
    else:
        text += f"• <b>Подпишись на</b> <a href='{link}'>{link}</a>\n"
    text += f"• <b>Награда:</b> {reward}⭐"
    await state.update_data(index=index)
    await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True,reply_markup= keyboard)


async def get_task_hander(message: Message,state: FSMContext,id):
    #await message.answer('затронул get_task_hander')
    print(f"[GET_TASK_HANDLER ]USERID   :_____ {message.from_user.id}")
    print(f"[DEBUG] SubgramList полностью: {SubgramList}")
    task = await get_first_available_task(id)  # Получаем список доступных заданий
    data = await state.get_data()
    index = data.get('index')   
    all_links = SubgramList.get(id, [])
    links = [item for item in all_links if not item.get("complete", False)]
    if not task and not links:
        await message.answer('Заданий пока нет. Задания появятся в ближайшее время.')
        return
    if not task:
        await test_subgram(message,state,id)
        return
    if task.type == 'subscribe':
        text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"

        if task.description:  # Проверяем, есть ли описание
            text += f"{task.description}\n\n"

        text += f"• <b>Подпишись на</b> <a href='{task.link}'>{task.link}</a>\n"
        text += f"• <b>Награда:</b> {task.reward}⭐"
        await state.update_data(task = task)
        reward = await count_reward(message.from_user.id)
        keyboard = await kb.complete_task_inline(task.link)
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
    elif task.type == 'entry':
        text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"

        if task.description:  # Проверяем, есть ли описание
            text += f"{task.description}\n\n"

        text += f"• <b>Подай заявку в канал</b> <a href='{task.link}'>{task.link}</a>\n"
        text += f"• <b>Награда:</b> {task.reward}⭐"
        await state.update_data(task = task)
        await create_task_state(message.from_user.id,task.id)
        reward = await count_reward(message.from_user.id)
        keyboard = await kb.entry_type_inline(task.link)
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
    elif task.type == 'BotEntry':
        text = f"🎯 <b>Доступно задание №{task.id}!</b>\n\n"

        if task.description:  # Проверяем, есть ли описание
            text += f"{task.description}\n\n"

        text += f"• <b>Перейдите в бота</b> <a href='{task.link}'>{task.link}</a>\n"
        text += f"• <b>Награда:</b> {task.reward}⭐"
        await state.update_data(task = task)
        reward = await count_reward(message.from_user.id)
        keyboard = await kb.complete_task_inline(task.link)
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
        BotEntry[message.from_user.id] = False
        await asyncio.sleep(5)
        BotEntry[message.from_user.id] = True