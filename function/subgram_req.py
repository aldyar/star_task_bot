from database.models import async_session
from database.models import User, Config, Task, TaskCompletion, Transaction,TaskHistory,TaskState
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime
import text as txt
from sqlalchemy import and_,func,not_
from aiogram import Bot
from aiogram.types import ChatMember
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.sql import exists
import aiohttp
from pprint import pprint 
from config import SUBGRAM_TOKEN
import asyncio
import json

def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner


class SubGramFunction:

    async def send_post(user_id,name,premium,gender):
        url = "https://api.subgram.ru/request-op/"  # заменишь на свой
        headers = {
            "Auth": SUBGRAM_TOKEN
        }
        data = {
            "UserId": user_id,
            "ChatId": user_id,
            "Gender": gender,
            "first_name": name,
            "language_code": "ru",
            "Premium": premium,
            "actions": "newtask"
        }
        print (data)
        async with aiohttp.ClientSession() as session:
            resp = await session.post(url, json=data, headers=headers)
            response_data = await resp.json()
            pprint(await resp.text())
            return response_data 


    async def get_unsubscribed_channel_links(response: dict):
        unsubscribed_links = []

        sponsors = response.get("additional", {}).get("sponsors", [])

        for sponsor in sponsors:
            if sponsor.get("status") == "unsubscribed":
                unsubscribed_links.append({
                    "link": sponsor.get("link"),
                    "type": sponsor.get("type"),
                    "complete": False
                })

        return unsubscribed_links
    
    # async def get_unsubscribed_channel_links(response: dict):
    #     unsubscribed_links = []

    #     sponsors = response.get("additional", {}).get("sponsors", [])

    #     for sponsor in sponsors:
    #         if sponsor.get("status") == "unsubscribed" and sponsor.get("type") == "channel":
    #             unsubscribed_links.append(sponsor.get("link"))

    #     return unsubscribed_links
    
    
    

    async def check_subscribe(link,user_id):
        url = "https://api.subgram.ru/get-user-subscriptions"  # заменишь на свой
        headers = {
            "Auth": SUBGRAM_TOKEN,
            "Content-Type": "application/json"
        }
        data = {
      "user_id": user_id,
      "links": [f"{link}"]
}
        async with aiohttp.ClientSession() as session:
            resp = await session.post(url, json=data, headers=headers)
            print(f"Response Status: {resp.status}")
            if resp.status == 200:
                response_data = await resp.json()
                print(f"Response Data: {response_data}")
                
                # Проверяем наличие подписок и их статус
                sponsors = response_data.get("additional", {}).get("sponsors", [])
                for sponsor in sponsors:
                    print(f"Checking sponsor: {sponsor}")
                    result = sponsor.get("status")
                    print (result)
                    return result
            else:
                print(f"Error: {resp.status}")
                
                return False
    
    @connection
    async def add_reward_user_subgram(session,user_id,reward):
        user = await session.scalar(select(User).where(User.tg_id == user_id))
        if user:
            user.balance += reward
            await session.commit()

    
    async def check_captcha(user_id: int, links: list[str]) -> bool:
        url = "https://api.subgram.ru/get-user-subscriptions"  # или другой нужный endpoint
        headers = {
            "Auth": SUBGRAM_TOKEN
        }
        data = {
            "user_id": user_id,
            "links": links
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as resp:
                response_data = await resp.json()
        
        print(f"[DEBUG] Response from Subgram:\n{json.dumps(response_data, indent=2, ensure_ascii=False)}")

        sponsors = response_data.get("additional", {}).get("sponsors", [])

        for sponsor in sponsors:
            status = sponsor.get("status")
            if status != "subscribed" and status != "notgetted":
                return False

        return True