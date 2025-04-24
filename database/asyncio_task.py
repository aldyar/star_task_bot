import asyncio
from asyncio import sleep
from function.event_req import EventFunction

async def event_watcher(bot):
    while True:
        await EventFunction.check_and_close_expired_events(bot)  # вызываем нашу функцию
        await sleep(3600)  # повторять раз в час
