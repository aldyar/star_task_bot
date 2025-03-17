from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.event.bases import TelegramObject
from aiogram.exceptions import TelegramBadRequest


class SubscriptionMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, channel_link: str):
        self.bot = bot
        self.channel_link = channel_link
        super().__init__()

    async def is_user_subscribed(self, user_id: int) -> bool:
        try:
            channel_username = self.channel_link.split("t.me/")[-1].strip("/")
            chat = await self.bot.get_chat(f'@{channel_username}')
            chat_id = chat.id

            member = await self.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            return member.status in ["member", "administrator", "creator"]
        
        except TelegramBadRequest:
            return False

    async def __call__(
        self, 
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], 
        event: TelegramObject, 
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id if isinstance(event, (Message, CallbackQuery)) else None
        if user_id:
            if not await self.is_user_subscribed(user_id):
                if isinstance(event, Message):
                    await event.answer(
                        f"❌ Вы не подписаны на канал! Подпишитесь, чтобы продолжить: {self.channel_link}",
                        disable_web_page_preview=True
                    )
                elif isinstance(event, CallbackQuery):
                    await event.message.answer(
                        f"❌ Вы не подписаны на канал! Подпишитесь, чтобы продолжить: {self.channel_link}",
                        disable_web_page_preview=True
                    )
                return  # Блокируем дальнейшую обработку
        return await handler(event, data)
