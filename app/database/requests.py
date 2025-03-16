from app.database.models import async_session
<<<<<<< HEAD
from app.database.models import User, Config, Task, TaskCompletion
=======
from app.database.models import User, Config, Task, TaskCompletion, Transaction
>>>>>>> 0845efb (Первый коммит)
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime
import text as txt
from sqlalchemy import and_


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
            referrer.referral_count += 1

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


@connection
async def edit_withdraw_limit(session, column_name: str, new_value: int):
    # Получаем текущий конфиг (должен быть один)
    config = await session.scalar(select(Config).where(Config.id == 1))
    
    if config:
        # Устанавливаем новое значение для переданной колонки
        setattr(config, column_name, new_value)
        
        # Сохраняем изменения
        await session.commit()


@connection
async def edit_bonus(session,bonus_amount):
    config = await session.scalar(select(Config).limit(1))  # Получаем объект Config, а не просто значение
    if config:
        config.bonus_amount = bonus_amount  # Изменяем значение `bonus_amount` в объекте Config
        await session.commit()  # Сохраняем изменения в базе данных


@connection
async def get_all_users(session):
    users = await session.scalars(select(User))
    return users.all()  # Возвращаем всех пользователей в виде списка


@connection
async def get_today_users(session):
    today = datetime.now().date()
    result = await session.execute(
        select(User)
        .where(User.register_date >= today)
        .order_by(User.referral_count.desc())  # Сортировка по количеству приглашений
    )
    return result.scalars().all()


@connection
async def get_all_users_date(session, date_1, date_2):
    # Преобразуем даты из строки в объект datetime
    date_1_obj = datetime.strptime(date_1, '%d-%m-%Y')
    date_2_obj = datetime.strptime(date_2, '%d-%m-%Y')
    
    # Запрос к БД с фильтрацией по дате регистрации
    query = select(User).where(
        and_(
            User.registration_date >= date_1_obj,
            User.registration_date <= date_2_obj
        )
    )
    
    result = await session.execute(query)
    users = result.scalars().all()
<<<<<<< HEAD
    return users
=======
    return users


@connection
async def create_transaction(session,tg_id, amount):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))

    new_transtaction = Transaction(
        tg_id = tg_id,
        username=user.username if user.username else None,
        amount = amount
    )
    user.balance -= amount

    session.add(new_transtaction)
    await session.commit()

@connection
async def get_pending_transactions(session):
    result = await session.execute(select(Transaction).where(Transaction.completed == False))
    return result.scalars().all()


@connection
async def complete_transaction(session, id):
    transaction = await session.scalar(select(Transaction).where(Transaction.id == id))
    if transaction:
        transaction.completed = True
        await session.commit()
>>>>>>> 0845efb (Первый коммит)
