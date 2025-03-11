from sqlalchemy import ForeignKey, String, BigInteger, DateTime, Boolean, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime


engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3',
                             echo=True)
    
    
async_session = async_sessionmaker(engine)


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

class Config(Base):
    __tablename__ = 'config'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bonus_amount: Mapped[float] = mapped_column(Float)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    link: Mapped[str] = mapped_column(String, nullable=False)  # Ссылка на задание
    reward: Mapped[float] = mapped_column(Float, nullable=False)  # Награда за выполнение
    total_completions: Mapped[int] = mapped_column(Integer, nullable=False)  # Заданный лимит выполнений
    completed_count: Mapped[int] = mapped_column(Integer, default=0)  # Сколько раз уже выполнили
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # Активно ли задание


class TaskCompletion(Base):
    __tablename__ = "task_completions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)  # Telegram ID пользователя
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)  # ID задания


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)