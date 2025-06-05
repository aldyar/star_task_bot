from database.models import async_session
from database.models import User, Config, Task, TaskCompletion, Transaction, TaskHistory
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime
import text as txt
from sqlalchemy import and_,func
from aiogram import Bot
from aiogram.types import ChatMember
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.orm import aliased


def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner


@connection
async def set_user(session, tg_id, username, referrer_id,lang):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    allowed_langs = ["ru", "en", "kk", "uk", "uz", "be"]

    if not user:
        #is_allowed_geo = lang.lower() in allowed_langs
        is_allowed_geo = lang is not None and lang.lower() in allowed_langs

    if not user:
        session.add(User(tg_id=tg_id, balance='1', username = username, referrer_id = referrer_id,lang=lang))
        referrer = await session.scalar(select(User).where(User.tg_id == referrer_id))
        ref_reward = await session.scalar(select(Config.ref_reward))
        if is_allowed_geo and referrer:
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
async def edit_start_text(session,text):
    config = await session.get(Config,1)
    if config:
        config.start_text = text
        await session.commit()


@connection
async def return_start_text(session):
    config = await session.get(Config,1)
    if config:
        config.start_text = txt.start
        await session.commit()



@connection 
async def create_task(session, link, reward, total_completions,chat_id,title, task_type, description=None):
    # if chat_id is None and title is None:
    #     chat_id = None
    #     title = None
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
            User.register_date >= date_1_obj,
            User.register_date <= date_2_obj
        )
    )
    
    result = await session.execute(query)
    users = result.scalars().all()
    return users


@connection
async def get_top_referrers_by_date(session, date_from, date_to):
    """
    Возвращает список пользователей, которые пригласили хотя бы 1 пользователя 
    в заданном промежутке дат, используя только tg_id.
    """
    date_1_obj = datetime.strptime(date_from, '%d-%m-%Y')
    date_2_obj = datetime.strptime(date_to, '%d-%m-%Y')
    Invited = aliased(User)  # пользователи, которые были приглашены

    stmt = (
        select(
            User.tg_id,
            User.username,
            func.count(Invited.id).label("invited_count")
        )
        .join(Invited, Invited.referrer_id == User.tg_id)
        .where(
            Invited.register_date >= date_1_obj,
            Invited.register_date <= date_2_obj
        )
        .group_by(User.tg_id, User.username)
        .having(func.count(Invited.id) > 0)
        .order_by(func.count(Invited.id).desc())
    )

    result = await session.execute(stmt)
    data = result.all()
    return data
    

@connection
async def create_transaction(session,tg_id, amount,lang):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))

    new_transaction = Transaction(
        tg_id = tg_id,
        username=user.username if user.username else None,
        amount = amount,
        user_lang = lang
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
        #print(f"Статус пользователя: {member.status}")
        
        is_subscribed = member.status in ["member", "administrator", "creator"]
        #print(f"Пользователь подписан: {is_subscribed}")
        
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

import time

@connection
async def check_subscriptions(session, bot: Bot):
    while True:
        #await bot.send_message(chat_id=1075213318, text='СТАРТ')
        start_time = time.time()
        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)
        penalty_count = 0
        penalty_entries = []  
        try:
            result = await session.execute(
                select(TaskCompletion).where(TaskCompletion.completed >= seven_days_ago)
            )
            task_completions = result.scalars().all()
            #await bot.send_message(chat_id=1075213318, text=f'Найдено {len(task_completions)} записей')

            # Загружаем все нужные Task'и одним запросом
            task_ids = {tc.task_id for tc in task_completions}
            task_result = await session.execute(select(Task).where(Task.id.in_(task_ids)))
            tasks = {task.id: task for task in task_result.scalars()}

            # Готовим пары (tg_id, chat_id)
            user_channel_pairs = []
            for tc in task_completions:
                task = tasks.get(tc.task_id)
                if task and task.type != 'BotEntry':
                    user_channel_pairs.append((tc.tg_id, task.chat_id))

            # Проверяем подписки пачкой
            subs_map = await batch_check_subscriptions(bot, user_channel_pairs)

            BATCH_SIZE = 50
            for i in range(0, len(task_completions), BATCH_SIZE):
                batch = task_completions[i:i + BATCH_SIZE]
                for tc in batch:
                    try:
                        task = tasks.get(tc.task_id)
                        if not task or task.type == 'BotEntry':
                            continue

                        is_subscribed = subs_map.get((tc.tg_id, task.chat_id), True)
                        if not is_subscribed and tc.is_subscribed:
                            penalty_count += 1
                            penalty_entries.append(f'tc.id={tc.id}, tg_id={tc.tg_id}, task_id={tc.task_id}')
                            user = await session.scalar(select(User).where(User.tg_id == tc.tg_id))
                            task_history = await session.scalar(
                                select(TaskHistory).where(
                                    TaskHistory.tg_id == tc.tg_id,
                                    TaskHistory.task_id == task.id
                                )
                            )

                            text = (
                                f"❌ *Вы только что отписались от канала* [@{task.title}]({task.link}) "
                                f"*и нарушили условие задания №{task.id}!*\n\n"
                                f"   *• С баланса в боте списано {task.reward}⭐*\n\n"
                                f"*Больше не отписывайтесь от каналов в заданиях, чтобы не получать штрафы!*"
                            )
                            if user:
                                #await bot.send_message(chat_id=1075213318, text=f"Обновляю баланс для {tc.tg_id}, списание⭐")
                                user.balance -= task.reward
                                tc.is_subscribed = False
                                if task_history:
                                    #await bot.send_message(chat_id=1075213318, text=f"Удаляю историю для {tc.tg_id}, task_id={task.id}")
                                    await session.delete(task_history)
                                #await bot.send_message(chat_id=1075213318, text=f"Удаляю task_completion для {tc.tg_id}, task_id={task.id}")
                                await session.delete(tc)
                                await session.flush()

                            try:
                                await bot.send_message(chat_id=tc.tg_id, text=text, parse_mode='Markdown', disable_web_page_preview=True)
                            except Exception as e:
                                #await bot.send_message(chat_id=1075213318,text=f"Не смог отправить сообщение пользователю {tc.tg_id}: {e}")
                                continue

                            

                    except Exception as e:
                        #await bot.send_message(chat_id=1075213318,text =f"Ошибка при обработке task_completion id={tc.id}: {e}")
                        print(f"Ошибка при обработке task_completion id={tc.id}: {e}")
                        continue

                #await bot.send_message(chat_id=1075213318, text=f'Обработано {i + len(batch)} из {len(task_completions)}')
            await session.commit()
            #await bot.send_message(chat_id=1075213318, text=f'🔁 Всего зашли в штрафной блок: {penalty_count}')
            chunk_size = 50
            for i in range(0, len(penalty_entries), chunk_size):
                chunk = penalty_entries[i:i + chunk_size]
                mess = "❌ Штрафы:\n" + "\n".join(chunk)
                #await bot.send_message(chat_id=1075213318, text=mess)

        except Exception as e:
            #await bot.send_message(chat_id=1075213318, text=f'Ошибка БД: {e}')
            print(f'Ошибка БД: {e}')
        elapsed_time = time.time() - start_time
        #await bot.send_message(chat_id=1075213318, text=f'Завершено за {elapsed_time:.2f} сек.')
        await asyncio.sleep(3)




async def batch_check_subscriptions(bot: Bot, user_channel_pairs: list[tuple[int, int]]) -> dict[tuple[int, int], bool]:
    result = {}
    for user_id, channel_id in user_channel_pairs:
        try:
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            result[(user_id, channel_id)] = member.status not in ('left', 'kicked')
        except Exception:
            result[(user_id, channel_id)] = False
    return result

@connection
async def test_fuck_func(session,bot: Bot):
    await bot.send_message(chat_id=1075213318, text='СТАРТ')
    start_time = time.time()  # Начинаем таймер
    tg_id =1075213318
    task_id = 7
    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)
    task_completions = await session.execute(
    select(TaskCompletion)
    .where(
        TaskCompletion.completed >= seven_days_ago,
        TaskCompletion.tg_id == 1075213318
    )
)
    task_completions = task_completions.scalars().all()
    for task_completion in task_completions:
        task = await session.scalar(select(Task).where(Task.id == task_completion.task_id))
        if not task:
                #print(f"Задание с ID {task_completion.task_id} не найдено.")
                continue
        elif task.type == 'BotEntry':
                continue
        is_subscribed = await is_user_subscribed(bot, tg_id, task.chat_id)
        if not is_subscribed and task_completion.is_subscribed:
                user = await session.scalar(select(User).where(User.tg_id == tg_id))
                task_history = await session.scalar(select(TaskHistory).where(TaskHistory.tg_id == tg_id, TaskHistory.task_id == task.id))
        
                text = (
                        f"❌ *Вы только что отписались от канала* [@{task.title}]({task.link}) *и нарушили условие задания №{task.id}!*\n\n"
                        f"   *• С баланса в боте списано {task.reward}⭐*\n\n"
                        f"*Больше не отписывайтесь от каналов в заданиях, чтобы не получать штрафы!*"
                        )
                try:
                    await bot.send_message(chat_id=tg_id, text=text, parse_mode='Markdown', disable_web_page_preview=True)
                except Exception as e:
                    print(f"Пользователь {tg_id} {e}")
                    continue
                if user:
                    user.balance -= task.reward
                    task_completion.is_subscribed = False
                    await session.delete(task_history)
                    await session.delete(task_completion)
                    await session.commit()
                end_time = time.time()  # Останавливаем таймер
                elapsed_time = end_time - start_time  # Вычисляем продолжительность
                await bot.send_message(chat_id=1075213318, text=str(elapsed_time), parse_mode='Markdown', disable_web_page_preview=True)


@connection
async def create_task_completions_history(session,tg_id, task_id):
    task = await session.scalar(select(Task).where(Task.id == task_id))
    new_task_comp = TaskCompletion(
        tg_id = tg_id,
        task_id = task_id
    )
    new_task_history = TaskHistory(
        tg_id = tg_id,
        task_id = task_id,
        chat_id = task.chat_id if task.chat_id is not None else 7777777


    )
    session.add(new_task_history)
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
    
    
@connection
async def set_image_url(session, url):
    config = await session.scalar(select(Config))
    config.image_link = url
    await session.commit()


@connection
async def delete_image_url(session):
    config = await session.scalar(select(Config))
    config.image_link = None
    await session.commit()

@connection
async def get_image_url(session):
    config = await session.scalar(select(Config).limit(1))
    image_url = config.image_link if config else None
    return image_url