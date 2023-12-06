import datetime


from sqlalchemy import BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from app.config import SQLALCHEMY_URL

engine = create_async_engine(SQLALCHEMY_URL, echo=True)

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):  # Base class for tables
    pass

class User(Base):                         # Table for users
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)

class Note(Base):                           # Table for notes
    __tablename__ = 'notes'

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()
    tg_id: Mapped[int] = mapped_column(BigInteger)
    reminder_time: Mapped[datetime.datetime] = mapped_column(DateTime)

async def async_main():                  # Function for creating tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def store_note(tg_id, note_text, reminder_time): # Function for storing notes
    async with async_session() as session:
        note = Note(text=note_text, tg_id=tg_id, reminder_time=reminder_time)
        session.add(note)
        await session.commit()
