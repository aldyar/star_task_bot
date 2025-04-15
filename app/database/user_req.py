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