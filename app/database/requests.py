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
async def set_user(session, tg_id, username, referrer_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))

    if not user:
        session.add(User(tg_id=tg_id, balance='1', username = username, referrer_id = referrer_id))
        await session.commit()
    
    elif user.referrer_id is None:
        user.referrer_id = referrer_id
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

@connection
async def get_withdraw_limit(session):
    result = await session.scalar(select(Config).limit(1))  # Получаем первую строку таблицы Config
    if result:
        return (
            result.withdraw_1,
            result.withdraw_2,
            result.withdraw_3,
            result.withdraw_4,
            result.withdraw_5,
            result.withdraw_6,
            result.withdraw_7,
        )
    return None  # Если таблица пуста

@connection
async def get_user(session,tg_id):
    result = await session.scalar(select(User).where(User.tg_id == tg_id))
    return result

@connection
async def set_referrer_id(session,tg_id, referrer_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))

    if user:
        user.referrer_id = referrer_id
        await session.commit()