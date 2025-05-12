from sqlalchemy import ForeignKey, String, BigInteger, DateTime, Boolean, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from datetime import datetime
from sqlalchemy import JSON


engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3',
                             echo=False)
    
    
async_session = async_sessionmaker(engine,class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(32), nullable=True)  # Username может отсутствовать
    balance: Mapped[float] = mapped_column(Float, default=0.0)  # Баланс с плавающей запятой
    referrer_id: Mapped[int] = mapped_column(BigInteger, nullable=True)  # ID рефера, может быть пустым
    bonus_update: Mapped[datetime] = mapped_column(DateTime, nullable=True)  
    register_date: Mapped[datetime] = mapped_column(DateTime,default=datetime.now)
    referral_count: Mapped[int] = mapped_column(Integer,default=0)
    task_count: Mapped[int] = mapped_column(Integer,default=1)
    gender: Mapped[str] = mapped_column(String,nullable=True)

class Config(Base):
    __tablename__ = 'config'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bonus_amount: Mapped[float] = mapped_column(Float)
    withdraw_1: Mapped[int] = mapped_column(Integer, default=15)
    withdraw_2: Mapped[int] = mapped_column(Integer, default=25)
    withdraw_3: Mapped[int] = mapped_column(Integer, default=50)
    withdraw_4: Mapped[int] = mapped_column(Integer, default=100)
    withdraw_5: Mapped[int] = mapped_column(Integer, default=150)
    withdraw_6: Mapped[int] = mapped_column(Integer, default=350)
    withdraw_7: Mapped[int] = mapped_column(Integer, default=500)
    start_text: Mapped[str] = mapped_column(String )
    ref_reward: Mapped[float] = mapped_column(Float)
    ref_text: Mapped[str] = mapped_column(String)
    image_link: Mapped[str] = mapped_column(String,nullable=True)
    reminder_text: Mapped[str] = mapped_column(String ,nullable=True)
    reminder_image:Mapped[str] = mapped_column(String,nullable=True)
    reminder_text_button:Mapped[str] = mapped_column(String,nullable=True)
    reminder_url_button:Mapped[str] = mapped_column(String,nullable=True)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    link: Mapped[str] = mapped_column(String, nullable=False)  # Ссылка на задание
    reward: Mapped[float] = mapped_column(Float, nullable=False)  # Награда за выполнение
    total_completions: Mapped[int] = mapped_column(Integer, nullable=False)  # Заданный лимит выполнений
    completed_count: Mapped[int] = mapped_column(Integer, default=0)  # Сколько раз уже выполнили
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # Активно ли задание
    chat_id: Mapped[int] = mapped_column(Integer,nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=True)
    title: Mapped[str] = mapped_column(String,nullable=True)    
    description: Mapped[str] = mapped_column(String, nullable=True)


class TaskHistory(Base):
    __tablename__ = 'task_history'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    task_id: Mapped[int] = mapped_column(Integer)
    chat_id: Mapped[int] = mapped_column(Integer)
    completed: Mapped[datetime] = mapped_column(DateTime,default=datetime.now())


class TaskCompletion(Base):
    __tablename__ = "task_completions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)  # Telegram ID пользователя
    task_id: Mapped[int] = mapped_column(Integer, nullable=False)  # ID задания
    completed: Mapped[datetime] = mapped_column(DateTime,default=datetime.now())
    is_subscribed : Mapped[bool] = mapped_column(Boolean, default=True)

class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=True)
    amount: Mapped[int] = mapped_column(Integer)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[datetime] = mapped_column(DateTime,default=datetime.now())
    message_id:Mapped[int] = mapped_column(Integer,nullable=True)

class TaskState(Base):
    __tablename__ = 'task_states'

    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    task_id: Mapped[int] = mapped_column(Integer, nullable=False)
    chat_id: Mapped[int] = mapped_column(Integer,nullable=True)

class Event(Base):
    __tablename__ = 'events'  

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String,nullable=True)
    c1: Mapped[int] = mapped_column(Integer,nullable=True)
    c2: Mapped[int] = mapped_column(Integer,nullable=True)
    c3: Mapped[int] = mapped_column(Integer,nullable=True)
    c4: Mapped[int] = mapped_column(Integer,nullable=True)
    c5: Mapped[int] = mapped_column(Integer,nullable=True)
    c6: Mapped[int] = mapped_column(Integer,nullable=True)
    rules: Mapped[int] = mapped_column(Integer,nullable=True)
    text: Mapped[str] = mapped_column(String)
    image: Mapped[str] = mapped_column(String,nullable=True)
    message_id: Mapped[int] = mapped_column(Integer,nullable=True)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)  
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)  
    participants: Mapped[str] = mapped_column(String, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean,default=True)

class StartChannel(Base):
    __tablename__ = 'start_channels'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(Integer,nullable=True)
    title: Mapped[str] = mapped_column(String,nullable=True)    
    link: Mapped[str] = mapped_column(String, nullable=True)

class LinkStat(Base):
    __tablename__ = 'links_stat'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    link_name: Mapped[str] = mapped_column(String,nullable=True)    
    clicks: Mapped[int] = mapped_column(Integer,default=0,nullable=True)
    done_captcha: Mapped[int] = mapped_column(Integer,default=0,nullable=True)
    premium: Mapped[int] = mapped_column(Integer,default=0,nullable=True)
    lang: Mapped[str] = mapped_column(String, nullable=True)
    users: Mapped[str] = mapped_column(String, nullable=True)
    capthca_users: Mapped[str] = mapped_column(String, nullable=True)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)