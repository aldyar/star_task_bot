from database.models import async_session
from database.models import User, Config, Task, TaskCompletion, Transaction,TaskHistory,TaskState, Event
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime, timedelta
import text as txt
from sqlalchemy import and_,func,not_
from aiogram import Bot
from aiogram.types import ChatMember
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.sql import exists
from config import ADMIN

def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner

class EventFunction:
    
    @connection
    async def create_event(session,c1,c2,c3,c4,c5,c6,type,rule,text,image,end_date):
        now = datetime.now()
        new_event = Event(
            c1 = c1,
            c2 = c2,
            c3 = c3 if c3 is not None else None,
            c4 = c4 if c4 is not None else None,
            c5 = c5 if c5 is not None else None,
            c6 = c6 if c6 is not None else None,
            rules = rule,
            type = type,
            text = text,
            image = image,
            end_date = end_date,
            start_date = now
        )
        session.add(new_event)
        await session.commit()


    @connection
    async def create_event_4(session,c1,c2,rule,text,image,end_date):
        new_event = Event(
            c1 = c1,
            c2 = c2,
            rules = rule,
            text = text,
            image = image,
            end_date = end_date
        )
        session.add(new_event)
        await session.commit()

    @connection
    async def check_active_event(session):
        event = await session.scalars(select(Event).where(Event.active == True))
        return event.first() is not None

    @connection
    async def get_active_event(session):
        event = await session.scalar(select(Event).where(Event.active == True))
        return event
    
    @connection
    async def check_user_referrals_in_event(session, tg_id) -> bool:
        # Получаем пользователя по tg_id
        event = await EventFunction.get_active_event()
        result = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return False

        # Считаем количество рефералов, зарегистрированных в период события
        result = await session.execute(
            select(func.count(User.tg_id)).where(
                User.referrer_id == user.tg_id,
                User.register_date >= event.start_date,
                User.register_date <= event.end_date
            )
        )
        referral_count = result.scalar()
        print(f"[DEBUG] Пользователь {user.tg_id} пригласил {referral_count} рефералов в период с {event.start_date} по {event.end_date}")
        print(f"[DEBUG] Требуется по правилу: {event.rules or 0}")  
        # Сравниваем с правилом
        return referral_count >= (event.rules or 0)


    @connection
    async def add_participant_to_event(session, tg_id,bot) -> bool:
    # Получаем событие
        event = await EventFunction.get_active_event()

        if not event:
            return False

        # Получаем текущий список участников
        current_participants = event.participants.split(",") if event.participants else []

        # Преобразуем user_id в строку для сравнения
        str_user_id = str(tg_id)

        # Если пользователь уже есть, ничего не делаем
        if str_user_id in current_participants:
            return True

        # Добавляем нового участника
        current_participants.append(str_user_id)
        updated_participants = ",".join(current_participants)
        await bot.send_message(tg_id,"🎉*Вы участвуете в конкурсе*" , parse_mode="Markdown")
        # Обновляем в базе
        await session.execute(
            update(Event)
            .where(Event.id == event.id)
            .values(participants=updated_participants)
        )
        await session.commit()
        return True
    
    @connection
    async def save_message_id(session,message_id):
        event = await session.scalar(select(Event).where(Event.active == True))

        if event:
            event.message_id = message_id
            await session.commit()

    @connection
    async def check_and_close_expired_events(session,bot:Bot):
        now = datetime.now()

        # Получаем все активные события, у которых уже прошёл end_date
        result = await session.execute(
            select(Event).where(
                Event.active == True,
                Event.end_date < now
            )
        )
        expired_events = result.scalars().all()

        for event in expired_events:
            event.active = False
            # Можешь тут добавить уведомление в канал или в лог
            for admin in ADMIN:
                await bot.send_message(
                admin,  # ID администратора
                f"Конкурс завершён! \nID Конкурса: {event.id}\nДата окончания: {event.end_date}\n\nОн был автоматически отключён."
            )
            await EventFunction.end_event_and_reward_users(bot,event.id)
        if expired_events:
            await session.commit()


    @connection
    async def delete_event(session,event_id):
        event = await session.scalar(select(Event).where(Event.id ==event_id))
        if event:
            await session.delete(event)
            await session.commit()

    @connection
    async def end_event_and_reward_users(session, bot: Bot, event_id: int):
        print(f"[1] Старт функции для event_id: {event_id}")
        event = await session.scalar(select(Event).where(Event.id == event_id))
        if not event:
            print(f"[2] Event с id={event_id} не найден.")
            return

        print(f"[3] Event найден: {event}")

        # Проверка участников
        if not event.participants:
            return

        print(f"[5] Получаем участников: {event.participants}")
        participants_ids = list(map(int, event.participants.split(",")))
        users = await session.execute(
            select(User).where(User.tg_id.in_(participants_ids))
        )
        users = users.scalars().all()
        print(f"[6] Получено пользователей: {len(users)}")

        # Считаем, сколько каждый пригласил людей в период конкурса
        user_stats = []
        for user in users:
            invited = await session.execute(
                select(User).where(
                    (User.referrer_id == user.tg_id) &
                    (User.register_date >= event.start_date) &
                    (User.register_date <= event.end_date)
                )
            )
            invited_list = invited.scalars().all()
            referral_count = len(invited_list)
            user_stats.append((user, referral_count))

        print(f"[7] Пользователи с количеством приглашённых в период конкурса: {[f'{u.username or u.tg_id}: {c}' for u, c in user_stats]}")

        # Сортируем по количеству приглашений
        user_stats.sort(key=lambda x: x[1], reverse=True)
        print(f"[8] Пользователи отсортированы по числу приглашённых.")

        users = [u for u, _ in user_stats]
        ref_counts = [c for _, c in user_stats]

        print(f"[9] Определение призов по типу: {event.type}")

        if event.type == "1":
            prizes = [event.c1, event.c2, event.c3] + [event.c4] * 17 + [event.c5] * 30 + [event.c6] * 50
        elif event.type == "2":
            prizes = [event.c1, event.c2, event.c3] + [event.c4] * 37 + [event.c5] * 60 + [event.c6] * 100
        elif event.type == "3":
            prizes = [event.c1, event.c2, event.c3] + [event.c4] * 97 + [event.c5] * 200 + [event.c6] * 200
        elif event.type == "4":
            prizes = [event.c1] * event.c2
        else:
            print(f"[10] Неизвестный тип ивента: {event.type}")
            return

        print(f"[11] Количество призов: {len(prizes)}")

        winners = []
        for i, user in enumerate(users[:len(prizes)]):
            prize = prizes[i]
            user.balance += prize
            winners.append(f"{i+1} место — @{user.username or user.tg_id} — +{prize}⭐️, пригласил: {ref_counts[i]}")
            print(f"[12] Присуждён приз {prize} пользователю @{user.username or user.tg_id}")

            try:
                await bot.send_message(user.tg_id, f"🎉 Поздравляем! Вы заняли {i+1} место и получили ⭐️{prize}.")
                print(f"[13] Сообщение отправлено пользователю @{user.username or user.tg_id}")
            except Exception as e:
                print(f"[14] Не удалось отправить сообщение пользователю @{user.username or user.tg_id}: {e}")

        await session.commit()
        print(f"[15] Баланс обновлён и коммит выполнен.")

        winner_text = "🏆 Итоги конкурса:\n\n" + "\n".join(winners)
        for admin in ADMIN:
            await bot.send_message(admin, winner_text)
            print(f"[16] Итоги конкурса отправлены админу.")


    @connection
    async def check_active_event_by_id(session,event_id):
        event = await session.scalar(select(Event).where(Event.id == event_id))
        if event:
            return event.active


    # @connection
    # async def end_event_and_reward_users(session, bot: Bot, event_id: int):
    #     print(f"[1] Старт функции для event_id: {event_id}")
    #     event = await session.scalar(select(Event).where(Event.id == event_id))
    #     if not event:
    #         print(f"[2] Event с id={event_id} не найден.")
    #         return

    #     print(f"[3] Event найден: {event}")

    #     # Проверка участников
    #     if not event.participants:
    #         return


    #     print(f"[5] Получаем участников: {event.participants}")
    #     participants_ids = list(map(int, event.participants.split(",")))
    #     users = await session.execute(
    #         select(User).where(User.tg_id.in_(participants_ids))
    #     )
    #     users = users.scalars().all()

    #     print(f"[6] Получено пользователей: {len(users)}")

    #     # Фильтруем по дате регистрации в период конкурса
    #     users = [u for u in users if event.start_date <= u.register_date <= event.end_date]
    #     print(f"[7] Пользователи после фильтра по дате регистрации: {len(users)}")
    #     # Сортировка по количеству приглашений (referral_count)
    #     users.sort(key=lambda x: x.referral_count, reverse=True)
    #     print(f"[8] Пользователи отсортированы по рефералам.")
    #     winners = []


    #     print(f"[9] Определение призов по типу: {event.type}")

    #     if event.type == "1":
    #         prizes = [event.c1, event.c2, event.c3] + [event.c4] * 17 + [event.c5] * 30 + [event.c6] * 50
    #     elif event.type == "2":
    #         prizes = [event.c1, event.c2, event.c3] + [event.c4] * 37 + [event.c5] * 60 + [event.c6] * 100
    #     elif event.type == "3":
    #         prizes = [event.c1, event.c2, event.c3] + [event.c4] * 97 + [event.c5] * 200 + [event.c6] * 200
    #     elif event.type == "4":
    #         prizes = [event.c1] * event.c2
    #     else:
    #         print(f"[10] Неизвестный тип ивента: {event.type}")
    #         return


    #     print(f"[11] Количество призов: {len(prizes)}")

    #     for i, user in enumerate(users[:len(prizes)]):
    #         prize = prizes[i]
    #         user.balance += prize
    #         winners.append(f"{i+1} место — @{user.username or user.tg_id} — +{prize}₸, пригласил: {user.referral_count}")
    #         print(f"[12] Присуждён приз {prize} пользователю @{user.username or user.tg_id}")

    #         try:
    #             await bot.send_message(user.tg_id, f"🎉 Поздравляем! Вы заняли {i+1} место и получили {prize}.")
    #             print(f"[13] Сообщение отправлено пользователю @{user.username or user.tg_id}")
    #         except Exception as e:
    #             print(f"[14] Не удалось отправить сообщение пользователю @{user.username or user.tg_id}: {e}")

    #     await session.commit()


    #     print(f"[15] Баланс обновлён и коммит выполнен.")
    #     winner_text = "🏆 Итоги конкурса:\n\n" + "\n".join(winners)
    #     await bot.send_message(1075213318, winner_text)
    #     print(f"[16] Итоги конкурса отправлены админу.")
