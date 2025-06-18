from database.models import async_session
from database.models import User, Config, Task, TaskCompletion, Transaction,TaskHistory,TaskState, Event,MiniAdd
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

class MiniAdds:

    @connection
    async def get_mini_add(session,type):
        mini_add = await session.scalars(select(MiniAdd).where(MiniAdd.type == type))
        result = mini_add.all()
        return result if result else None
        
    
    @connection
    async def set_mini_add(session,type,text,button_text,url):
        # mini_add = await session.scalar(select(MiniAdd).where(MiniAdd.type == type))
        # if mini_add:
        #     mini_add.text = text
        #     mini_add.type = type
        #     mini_add.button_text = button_text
        #     mini_add.url = url
        # else:
        new_add = MiniAdd(
                        type=type,
                        text=text,
                        button_text=button_text,
                        url=url
                    )
        session.add(new_add)
        await session.commit()

    @connection
    async def delete_mini_adds(session,id):
        mini_add = await session.scalar(select(MiniAdd).where(MiniAdd.id == id))
        if mini_add:
            await session.delete(mini_add)
            await session.commit()