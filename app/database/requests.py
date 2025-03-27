from app.database.models import async_session
from app.database.models import User, Config, Task, TaskCompletion, Transaction
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime
import text as txt
from sqlalchemy import and_,func
from aiogram import Bot
from aiogram.types import ChatMember
from aiogram.exceptions import TelegramBadRequest


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
    result = await session.execute(select(Task).where(Task.is_active == True))
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
async def create_task(session, link, reward, total_completions,chat_id,title, task_type, description=None):
    new_task = Task(
        link=link,
        reward=reward,
        total_completions=total_completions,
        chat_id = chat_id,
        title = title,
        type = task_type,
        description = description
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
    return users


@connection
async def create_transaction(session,tg_id, amount):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))

    new_transaction = Transaction(
        tg_id = tg_id,
        username=user.username if user.username else None,
        amount = amount
    )
    user.balance -= amount

    session.add(new_transaction)
    await session.commit()
    await session.refresh(new_transaction)  # Привязываем объект к сессии перед возвратом
    return new_transaction  # Теперь можно возвращать весь объект

@connection
async def insert_message_id(session,id , message_id):
    transaction = await session.scalar(select(Transaction).where(Transaction.id == id))
    if transaction:
        transaction.message_id = message_id
        await session.commit()

@connection
async def get_transaction(session,id):
    transaction = await session.scalar(select(Transaction).where(Transaction.id == id))
    return transaction

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
        return True
    return False


@connection
async def find_active_task_from(session, start_id: int):
    # Проверяем сразу указанную id
    result = await session.execute(
        select(Task).where(Task.id == start_id, Task.is_active == True)
    )
    task = result.scalars().first()
    
    if task:
        return task  # Если задание активно, возвращаем его
    #elif not task:
        #return False
    # Если задание не активно, продолжаем искать дальше 
    current_id = start_id + 1
    
    # Получаем максимальный ID существующего задания
    max_id = await session.scalar(select(Task.id).order_by(Task.id.desc()))
    
    while current_id <= max_id:
        result = await session.execute(
            select(Task).where(Task.id == current_id, Task.is_active == True)
        )
        task = result.scalars().first()
        
        if task:
            return task  # Возвращаем найденное активное задание
        
        current_id += 1  # Увеличиваем id и продолжаем поиск
    
    # Если активных заданий не найдено, возвращаем None
    return None


@connection
async def get_task_about_taskid(session,task_id):
    task = await session.scalar(select(Task).where(Task.id == task_id))
    return task


@connection
async def get_task(session, tg_id: int):
    task_count = await session.scalar(select(User.task_count).where(User.tg_id == tg_id))

    task = await find_active_task_from(task_count)
    if not task:  # Если задание не найдено
        return None

    result = await session.scalar(select(Task).where(Task.id == task.id))
    return result


async def is_user_subscribed(bot: Bot, user_id: int, chat_id) -> bool:
    try:
        """print(f"\nПроверка подписки пользователя {user_id} на канал {channel_link}")
        
        # Извлекаем имя канала из ссылки
        channel_username = channel_link.split("t.me/")[-1].strip("/")
        print(f"Имя канала: {channel_username}")
        
        # Получаем информацию о чате
        chat = await bot.get_chat(f'@{channel_username}')
        chat_id = chat.id
        print(f"ID чата: {chat_id}")"""
        
        # Проверяем статус пользователя в чате
        member: ChatMember = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        print(f"Статус пользователя: {member.status}")
        
        is_subscribed = member.status in ["member", "administrator", "creator"]
        print(f"Пользователь подписан: {is_subscribed}")
        
        return is_subscribed
        
    except TelegramBadRequest as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False
    

@connection
async def completed_task (session,task_id, tg_id, amount):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    task = await session.scalar(select(Task).where(Task.id == task_id))

    if task and user:
        user.balance += amount
        user.task_count =task_id + 1
        task.total_completions -=1
        task.completed_count +=1

        if task.total_completions <= 0:
            task.is_active = False
            await session.commit()
            return True  # Возвращаем True, если total_completions стал 0
    
    await session.commit()
    return False  # Возвращаем False, если task еще активен



import asyncio
from datetime import datetime, timedelta


async def send_notification(bot: Bot, user_id: int, text: str):
    try:
        await bot.send_message(chat_id=user_id, text=text)
    except Exception as e:
        print(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")


@connection
async def check_subscriptions(session, bot: Bot):
    while True:
        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)

        #print(f"\n--- Проверка подписок начата. Время: {now} ---")

        try:
            # Получаем все записи TaskCompletion
            task_completions = await session.execute(
                select(TaskCompletion)
                .where(TaskCompletion.completed >= seven_days_ago)
            )
            task_completions = task_completions.scalars().all()
            #print(f"Найдено записей для проверки: {len(task_completions)}")

            for task_completion in task_completions:
                user_id = task_completion.tg_id
                task = await session.scalar(select(Task).where(Task.id == task_completion.task_id))
                
                if not task:
                    #print(f"Задание с ID {task_completion.task_id} не найдено.")
                    continue
                
                #print(f"\nПроверка пользователя {user_id} на подписку на канал {task.link}")

                try:
                    is_subscribed = await is_user_subscribed(bot, user_id, task.chat_id)
                    #print(f"Результат проверки подписки: {is_subscribed}")
                except Exception as e:
                    #print(f"Ошибка при проверке подписки пользователя {user_id}: {e}")
                    continue

                if not is_subscribed and task_completion.is_subscribed:
                    user = await session.scalar(select(User).where(User.tg_id == user_id))
                    channel_username = task.link.split("t.me/")[-1].strip("/")
                    text = (
                            f"❌ *Вы только что отписались от канала* [@{task.title}]({task.link}) *и нарушили условие задания №{task.id}!*\n\n"
                            f"   *• С баланса в боте списано {task.reward}⭐*\n\n"
                            f"*Больше не отписывайтесь от каналов в заданиях, чтобы не получать штрафы!*"
                            )
                    await bot.send_message(chat_id=user_id, text=text,parse_mode='Markdown', disable_web_page_preview=True)

                    if user:
                        user.balance -= task.reward
                        task_completion.is_subscribed = False
                        await session.commit()
                elif is_subscribed and not task_completion.is_subscribed:
                    user = await session.scalar(select(User).where(User.tg_id == user_id))
                    channel_username = task.link.split("t.me/")[-1].strip("/")
                    text = (
                            f"✅ *Спасибо за повторную подписку на канал* [@{task.title}]({task.link})!\n\n"
                            f"   *• На ваш баланс в боте добавлено {task.reward}⭐️*\n\n"
                            f"*Продолжайте оставаться подписанным, чтобы не терять свои баллы!*"
                            )
                    await bot.send_message(chat_id=user_id, text=text, parse_mode='Markdown', disable_web_page_preview=True)

                    if user:
                        user.balance += task.reward
                        task_completion.is_subscribed = True
                        await session.commit()
        except Exception as e:
            print(f"Ошибка при выполнении запроса к БД: {e}")

        print(f"--- Проверка подписок завершена. Ожидание 24 часа. ---")
        await asyncio.sleep(3)


@connection
async def create_task_completions(session,tg_id, task_id):
    new_task_comp = TaskCompletion(
        tg_id = tg_id,
        task_id = task_id
    )
    session.add(new_task_comp)
    await session.commit()


@connection
async def check_user(session, user_id):
    user = await session.scalar(select(User).where(User.tg_id == user_id))
    if user:
        return True
    else: 
        return False
    

@connection
async def count_reward(session, tg_id):
    # Находим task_count пользователя по tg_id
    task_count = await session.scalar(select(User.task_count).where(User.tg_id == tg_id))

    if task_count is None:
        return 0.0  # Если пользователь не найден, возвращаем 0

    # Находим и суммируем все значения reward активных заданий
    total_reward = await session.scalar(
        select(func.sum(Task.reward))
        .where(Task.is_active == True)
    )

    return total_reward if total_reward is not None else 0.0  # Возвращаем сумму активных заданий или 0


@connection
async def join_request(session,user_id,chat_id):
    task = await session.scalar(select(Task).where(Task.chat_id == chat_id,Task.is_active == True))
    if task:
        await completed_task(task.id,user_id,task.reward)
        return True 
    

@connection
async def skip_task(session, user_id, task_id):
    user = await session.scalar(select(User).where(User.tg_id == user_id))
    if user:
        user.task_count += 1
        task = await find_active_task_from(user.task_count)
        await session.commit()
        return task
    else:
        return False
    
    