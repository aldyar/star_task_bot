from app.database.models import async_session
from app.database.models import User, Config, Task, TaskCompletion, Transaction,TaskHistory
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
    return task
