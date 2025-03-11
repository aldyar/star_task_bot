from app.database.models import async_session
from app.database.models import User, Config, Task, TaskCompletion
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime

def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner


@connection
async def set_user(session, tg_id, username):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))

    if not user:
        session.add(User(tg_id=tg_id, balance='1', username = username))
        await session.commit()


@connection
async def get_config(session,field):
    result = await session.scalar(select(getattr(Config, field)))
    return result


@connection
async def get_bonus_update(session, tg_id: int):
    result = await session.scalar(
        select(User.bonus_update).where(User.tg_id == tg_id)
    )
    return result


@connection
async def update_bonus(session, tg_id, now, bonus):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))

    if user:
        user.balance += bonus
        user.bonus_update = now
        await session.commit()


"""@connection
async def check_tasks(session, tg_id):
    # Получаем все ID активных заданий
    active_task_ids = await session.scalars(
        select(Task.id).where(Task.is_active == True)
    )
    active_task_ids = set(active_task_ids.all())  # Преобразуем в множество

    # Получаем ID заданий, которые уже были выполнены пользователем
    completed_task_ids = await session.scalars(
        select(TaskCompletion.task_id).where(TaskCompletion.tg_id == tg_id)
    )
    completed_task_ids = set(completed_task_ids.all())  # Преобразуем в множество

    # Вычисляем задания, которые еще не были выполнены пользователем
    available_tasks = active_task_ids - completed_task_ids

    return list(available_tasks)
"""

@connection
async def check_tasks(session, tg_id):
    # Запрашиваем задания, которые активны и не были выполнены пользователем
    active_tasks = await session.scalars(
        select(Task)
        .where(
            Task.is_active == True,
            Task.id.notin_(
                select(TaskCompletion.task_id)
                .where(TaskCompletion.tg_id == tg_id)
            )
        )
    )
    return list(active_tasks.all())  # Возвращаем список объектов Task
