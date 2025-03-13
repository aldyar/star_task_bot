from app.database.models import async_session
from app.database.models import User, Config, Task, TaskCompletion
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime
import text as txt


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
        referrer = await session.scalar(select(User).where(User.tg_id == referrer_id))
        ref_reward = await session.scalar(select(Config.ref_reward))
        if referrer:
            referrer.balance += ref_reward

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
async def get_all_tasks(session):
    result = await session.execute(select(Task))
    return result.scalars().all()


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


@connection
async def create_config(session):
    existing_config = await session.get(Config, 1)
    
    if existing_config:
        return
    
    new_config = Config(
        bonus_amount = 1.0,
        start_text = txt.start,
        ref_reward = 2.0,
        ref_text = txt.ref
    )

    session.add(new_config)
    await session.commit()

@connection
async def get_task(session, task_id):
    task = await session.scalar(select(Task).where(Task.id == task_id))
    return task


@connection
async def edit_task_reward(session, task_id, reward):
    task = await session.scalar(select(Task).where(Task.id == task_id))
    if task:
        task.reward = reward
        await session.commit()


@connection 
async def edit_task_active(session,task_id):
    task = await session.scalar(select(Task).where(Task.id == task_id))
    if task:
        task.is_active = False
        await session.commit()


@connection
async def edit_task_total_completion(session, task_id, content):
    task = await session.scalar(select(Task).where(Task.id == task_id))
    if task:
        task.total_completions += content
        await session.commit()


@connection
async def edit_ref_text(session, text):
    config = await session.get(Config, 1)  # Предполагаем, что у тебя есть запись с id=1
    if config:
        config.ref_text = text  # Меняем текст в базе
        await session.commit()  # Сохраняем изменения


@connection
async def edit_ref_reward(session, reward):
    config = await session.get(Config,1)
    if config:
        config.ref_reward = reward
        await session.commit()

@connection 
async def create_task(session, link, reward, total_completions):
    new_task = Task(
        link=link,
        reward=reward,
        total_completions=total_completions
    )   
    session.add(new_task)
    await session.commit()