from app.database.models import async_session
from app.database.models import User, Config, Task, TaskCompletion, Transaction,TaskHistory,TaskState
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime
import text as txt
from sqlalchemy import and_,func,not_
from aiogram import Bot
from aiogram.types import ChatMember
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.sql import exists


def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner


@connection
async def get_first_available_task(session, tg_id):
    task = await session.scalar(select(Task).where(Task.is_active == True,not_(exists().where(and_(TaskHistory.task_id == Task.id, TaskHistory.tg_id == tg_id)))).order_by(Task.id))
    return task


@connection
async def skip_task_function(session, tg_id, task_id):
    task = await session.scalar(
        select(Task)
        .where(
            Task.is_active == True,
            Task.id > task_id,  # Начинаем поиск с заданного task_id
            not_(
                exists().where(
                    and_(TaskHistory.task_id == Task.id, TaskHistory.tg_id == tg_id)
                )
            )
        )
        .order_by(Task.id)  # Сортируем по ID, чтобы вернуть самое первое
    )
    if not task:
            task = await session.scalar(select(Task).where(Task.is_active == True,not_(exists().where(and_(TaskHistory.task_id == Task.id, TaskHistory.tg_id == tg_id)))).order_by(Task.id))

    return task


@connection
async def create_task_state(session,tg_id,task_id):
    state = await session.scalar(select(TaskState).where(TaskState.tg_id == tg_id))
    if not state:
        new_task_state = TaskState(
             tg_id = tg_id,
             task_id = task_id
        )
        session.add(new_task_state)
        await session.commit()
    elif state:
        state.task_id = task_id
        await session.commit()


@connection
async def get_task_state(session,tg_id):
    task = await session.scalar(select(TaskState).where(TaskState.tg_id == tg_id))
    return task


@connection
async def create_task_history(session,tg_id,task_id,chat_id):
    new_task_history = TaskHistory(
        tg_id = tg_id,
        task_id = task_id,
        chat_id = chat_id
    )
    session.add(new_task_history)
    await session.commit()


@connection
async def get_task_history(session,tg_id, task_id):
    task_history = await session.scalar(select(TaskHistory).where(TaskHistory.tg_id == tg_id, TaskHistory.task_id == task_id))
    return task_history


@connection
async def check_entry_task_history(session,tg_id,task_id):
    task_history = await get_task_history(tg_id,task_id)
    if task_history:
        return False
    else:
        return True
    
@connection
async def get_archive_task(session):
    tasks = await session.scalars(select(Task).where(Task.is_active == False))
    if tasks:
        return tasks
    

@connection
async def activate_task(session,task_id):
    task = await session.scalar(select(Task).where(Task.id == task_id))
    if task:
        task.is_active = True
        await session.commit()


    