from app.database.models import async_session
from app.database.models import User, Config, Task, TaskCompletion, Transaction,TaskHistory,TaskState, Event,StartChannel
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

class StartChannelFunction:

    @connection 
    async def get_channels(session):
        result = await session.scalars(select(StartChannel))
        channels = result.all()
        return channels if channels else False
    

    @connection
    async def set_channels(session,chat_id,title,link):
        new_channel = StartChannel(
            chat_id = chat_id,
            title = title,
            link = link
        )
        session.add(new_channel)
        await session.commit()

    async def is_bot_admin(bot: Bot, chat_id: int) -> bool:
        try:
            bot_member = await bot.get_chat_member(chat_id, bot.id)

            if isinstance(bot_member, (ChatMemberAdministrator, ChatMemberOwner)):
                return True
            return False

        except (TelegramBadRequest, TelegramForbiddenError):
            # Бот не может получить информацию о чате (например, не добавлен)
            return False
        
    @connection
    async def delete_channel(session,id):
        channel = await session.scalar(select(StartChannel).where(StartChannel.id == id))
        if channel:
            await session.delete(channel)
            await session.commit()

    @connection
    async def is_user_subscribed(session, bot: Bot, user_id: int) -> bool:
        result = await session.scalars(select(StartChannel))
        channels = result.all()

        for channel in channels:
            try:
                member: ChatMember = await bot.get_chat_member(chat_id=channel.chat_id, user_id=user_id)
                if member.status not in ["member", "administrator", "creator"]:
                    return False
            except Exception as e:
                # например, если бот не админ в этом канале или канал не существует
                print(f"Ошибка при проверке подписки на канал {channel.chat_id}: {e}")
                return False

        return True
