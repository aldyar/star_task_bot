from app.database.models import async_session
from app.database.models import User, Config, Task, TaskCompletion, Transaction,TaskHistory,TaskState
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime, timedelta
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


class UserFunction:

    @connection
    async def get_referral_count_by_days(session,tg_id, days):
        # Сначала найдем пользователя по tg_id
        result = await session.execute(
            select(User.tg_id).where(User.tg_id == tg_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return 0  # Если пользователя не нашли

        # Вычисляем дату отсечки
        cutoff_date = datetime.now() - timedelta(days=days)

        # Считаем количество рефералов, которые зарегистрировались за последние N дней
        result = await session.execute(
            select(func.count()).where(
                User.referrer_id == user,
                User.register_date >= cutoff_date
            )
        )

        return result.scalar() or 0
    

    @connection
    async def get_referral(session,tg_id):
        referrals = await session.scalars(select(User).where(User.referrer_id == tg_id))
        return referrals
    


    @connection
    async def get_user_top_5_referrers(session, days: int):
        """
        Возвращает топ-5 пользователей по количеству приведённых рефералов за последние `days` дней.
        Использует только tg_id. Возвращает: [(tg_id, username или "Без username", кол-во рефералов), ...]
        """
        start_date = datetime.now() - timedelta(days=days)

        # Считаем количество пользователей, которых привёл каждый реферер (по tg_id)
        stmt = (
            select(User.referrer_id, func.count(User.id).label("ref_count"))
            .where(User.referrer_id.isnot(None), User.register_date >= start_date)
            .group_by(User.referrer_id)
            .order_by(func.count(User.id).desc())
            .limit(5)
        )

        result = await session.execute(stmt)
        top_data = result.all()  # [(referrer_tg_id, count), ...]

        if not top_data:
            return []

        ref_tg_ids = [tg_id for tg_id, _ in top_data]

        # Получаем пользователей по tg_id
        users_stmt = select(User).where(User.tg_id.in_(ref_tg_ids))
        users_result = await session.execute(users_stmt)
        users = {user.tg_id: user for user in users_result.scalars()}

        # Формируем результат
        final_result = []
        for tg_id, count in top_data:
            user = users.get(tg_id)
            if user:
                username = user.username if user.username else "Без username"
                final_result.append((tg_id, username, count))

        return final_result
    
    @connection
    async def get_user_refferal_count(session,tg_id,days):
        start_date = datetime.now() - timedelta(days)
        count = await session.scalar(
            select(func.count(User.tg_id))
             .where(User.referrer_id == tg_id, User.register_date >= start_date)
         )

        return count