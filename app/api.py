from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
from config import SUBGRAM_TOKEN,TOKEN
from aiogram import Bot
from fastapi.responses import JSONResponse
import asyncio
from function.user_req import UserFunction
app = FastAPI()
bot = Bot(token=TOKEN)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}

@app.get("/ping")
async def ping():
    return {"status": "ok"}

class Webhook(BaseModel):
    webhook_id: int
    link: str
    user_id: int
    bot_id: int
    status: str
    subscribe_date: str

class WebhooksPayload(BaseModel):
    webhooks: List[Webhook]

@app.post("/webhooks")
async def receive_webhooks(
    payload: WebhooksPayload,
    api_key: Optional[str] = Header(None, alias="Api-Key"),
    cf_worker: Optional[str] = Header(None, alias="Cf-Worker"),
    content_type: Optional[str] = Header(None, alias="Content-Type")
):
    print('METODD ZATRONUT')
    if api_key != SUBGRAM_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    if content_type != "application/json":
        raise HTTPException(status_code=400, detail="Invalid Content-Type")

    # Быстро отвечаем
    asyncio.create_task(process_webhook(payload))
    return JSONResponse(content={"status": "ok"}, status_code=200)

async def process_webhook(payload: WebhooksPayload):
    #message = "Processed Webhooks:\n"
    for hook in payload.webhooks:
        #message += f"Webhook ID: {hook.webhook_id}, Status: {hook.status}, Message: Processed webhook for user {hook.user_id}\n"
        text = (
                        f"❌ *Вы только что отписались от канала* [@{hook.link}]({hook.link}) *и нарушили условие задания!*\n\n"
                        f"   *• С баланса в боте списано 0.25 ⭐*\n\n"
                        f"*Больше не отписывайтесь от каналов в заданиях, чтобы не получать штрафы!*"
                        )
        await UserFunction.user_away_reward(hook.user_id,0.25)
        await bot.send_message(chat_id =hook.user_id, text =text,parse_mode='Markdown', disable_web_page_preview=True)

