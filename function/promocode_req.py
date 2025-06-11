from database.models import async_session
from database.models import User, Promocode
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime, timedelta
import text as txt
from sqlalchemy import and_,func,not_
from aiogram import Bot
from aiogram.types import ChatMember
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.sql import exists
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner


def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner

class PromocodeFunction:
    
    @connection
    async def get_promo(session,code):
        promo = await session.scalar(select(Promocode).where(Promocode.code == code))
        if promo:
            return promo
        
        
    @connection
    async def get_promocode(session):
        promocodes = await session.scalars(select(Promocode))
        return promocodes.all()


    @connection
    async def create_promocode(session,name,promocode,count,reward):
        new_promocode = Promocode(
            name = name,
            code = promocode,
            total_count = count,
            reward = reward,
            use_count = 0
        )
        session.add(new_promocode)
        await session.commit()


    @connection
    async def delete_promocode(session,code):
        promocode = await session.scalar(select(Promocode).where(Promocode.code == code))
        if promocode:
            await session.delete(promocode)
            await session.commit()
            return True
        else:
            return False


    @connection
    async def use_promocode(session,code,user_id):
        promocode = await session.scalar(select(Promocode).where(Promocode.code == code))
        user = await session.scalar(select(User).where(User.tg_id == user_id))
        if not promocode:
            return 1 #Промокод не найден
        if promocode.total_count == promocode.use_count:
            return 2 #Промокод не действителен
        users_list = promocode.users.split(',') if promocode.users else []
        if str(user_id) in users_list:
            return 3  # Пользователь уже использовал промокод
        
        users_list.append(str(user_id))
        promocode.users = ','.join(users_list)
        promocode.use_count += 1
        user.balance += promocode.reward
        await session.commit()
        return 5 # Все ок