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
from database.models import LinkStat
import json

def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner


class LinkFunction:

    @connection
    async def set_link(session,link_name):
        new_link = LinkStat(
            link_name = link_name
        )
        session.add(new_link)
        await session.commit()


    @connection
    async def count_link(session,link_name,premium,lang,user_id):

        link = await session.scalar(select(LinkStat).where(LinkStat.link_name == link_name))
        if link:
            # --- Проверка user_id в поле users ---
            existing_users = link.users.split(",") if link.users else []
            if str(user_id) in existing_users:
                return  # Уже есть — не продолжаем
            
            link.clicks +=1
            if premium:
                link.premium +=1
            lang_stats = {}
            if link.lang:
                try:
                    lang_stats = json.loads(link.lang)
                except json.JSONDecodeError:
                    # если что-то пошло не так (битые данные), просто сбрасываем
                    lang_stats = {}

            # Обновляем счётчик для текущего языка
            if lang in lang_stats:
                lang_stats[lang] += 1
            else:
                lang_stats[lang] = 1

            # Обратно сохраняем в строку
            link.lang = json.dumps(lang_stats)
            # Добавление нового user_id в users
            existing_users.append(str(user_id))
            link.users = ",".join(existing_users)
            await session.commit()

    @connection
    async def count_done_captcha(session,link_name,user_id):
        link = await session.scalar(select(LinkStat).where(LinkStat.link_name == link_name))
        if link:
            # --- Проверка user_id в поле users ---
            existing_users = link.capthca_users.split(",") if link.capthca_users else []
            if str(user_id) in existing_users:
                return  # Уже есть — не продолжаем
            link.done_captcha +=1
            # Добавление нового user_id в users
            existing_users.append(str(user_id))
            link.capthca_users = ",".join(existing_users)
            await session.commit()


    @connection
    async def get_link(session,link_name):
        link = await session.scalar(select(LinkStat).where(LinkStat.link_name == link_name))
        return link
    
    @connection
    async def get_links(session):
        result = await session.scalars(select(LinkStat))
        return result.all()
    
    @connection
    async def count_done_our_captcha(session,link_name,user_id):
        link = await session.scalar(select(LinkStat).where(LinkStat.link_name == link_name))
        if link:
            # --- Проверка user_id в поле users ---
            existing_users = link.capthca_users.split(",") if link.capthca_users else []
            if str(user_id) in existing_users:
                return  # Уже есть — не продолжаем
            link.done_captcha +=1
            link.count_captcha +=1
            # Добавление нового user_id в users
            existing_users.append(str(user_id))
            link.capthca_users = ",".join(existing_users)
            await session.commit()

