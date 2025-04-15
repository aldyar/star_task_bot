from app.database.models import async_session
from app.database.models import User, Config, Task, TaskCompletion, Transaction, TaskHistory
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime
import text as txt
from sqlalchemy import and_,func
from aiogram import Bot
from aiogram.types import ChatMember
from aiogram.exceptions import TelegramBadRequest
import json


def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner
class ReminderFunction:

    
    @connection
    async def get_config_reminder_text(session):
        text = await session.scalar(select(Config.reminder_text))
        if text:
            return text
        
    
    @connection
    async def get_config_reminder_image(session):
        image = await session.scalar(select(Config.reminder_image))
        if image:
            return image


    @connection
    async def set_reminder_text(session,text):
        config = await session.scalar(select(Config))
        if config:
            config.reminder_text = text
            await session.commit()


    @connection
    async def set_reminder_image(session,url):
        config = await session.scalar(select(Config))
        if config:
            config.reminder_image = url
            await session.commit()

    @connection
    async def delete_image(session):
        config = await session.scalar(select(Config))
        if config:
            config.reminder_image = None
            await session.commit()



























#НЕУДАЧНАЯ ПОПЫТКА СДЕЛАТЬ В JSON
########################################################################################################################
########################################################################################################################
########################################################################################################################




    # @connection
    # async def get_config_reminder_text(session):
    #     reminder = await session.scalar(select(Config.reminder))
    #     if reminder and "text" in reminder:
    #         reminder_dict = json.loads(reminder)
    #         return reminder_dict.get("text", "")
    #     return None
    
    # @connection
    # async def get_config_reminder_image_link(session):
    #     reminder = await session.scalar(select(Config.reminder))
    #     if reminder and "image_link" in reminder:
    #         reminder_dict = json.loads(reminder)
    #         return reminder_dict.get("image_link", "")
    #     return None


    # @connection
    # async def set_reminder_text(session, text):
    #     config = await session.scalar(select(Config).limit(1))
    #     if config:
    #         reminder_data = config.reminder or {}
    #         reminder_data["text"] = text
    #         config.reminder = reminder_data
    #     await session.commit()

    # # @connection
    # # async def set_reminder_image(session, link):
    # #     print(f'SSSSSSSSSSSSSSULKA:{link}')
    # #     config = await session.scalar(select(Config).limit(1))
    # #     print(config)  # Выведем конфиг, чтобы проверить его значение
    # #     if config:
    # #         reminder_data = config.reminder or {}  # Если reminder пустой, создаем пустой dict
    # #         reminder_data["image_link"] = link
    # #         config.reminder = reminder_data  # Обновляем reminder
    # #         await session.commit()  # Сохраняем изменения
    # #         print("Reminder image link updated.")  # Добавил вывод для проверки
    # #     else:
    # #         print("Config not found.")  # На случай, если config не найден

    # @connection
    # async def set_reminder_image(session, link):
    #     try:
    #         config = await session.scalar(select(Config).limit(1))
    #         if config:
    #             # Получаем текущее значение reminder
    #             reminder_data = config.reminder or {}

    #             # Обновляем ключ внутри словаря
    #             reminder_data["image_link"] = link

    #             # Назначаем обратно, чтобы SQLAlchemy отследил изменение
    #             config.reminder = reminder_data
    #             await session.merge(config)
    #             # Сохраняем
    #             await session.commit()

    #             print("✅ Image link в reminder обновлён!")
    #         else:
    #             print("❌ Config не найден")
    #     except Exception as e:
    #         await session.rollback()
    #         print(f'Произошла ошибка при вставке данных => {e}')
   
    
    # @connection
    # async def delete_image_url(session):
    #     config = await session.scalar(select(Config).limit(1))
    #     if config and isinstance(config.reminder, dict):
    #         reminder_data = config.reminder.copy()
    #         reminder_data.pop("image_link", None)  # удаляет ключ, если он есть
    #         config.reminder = reminder_data
    #     await session.commit()