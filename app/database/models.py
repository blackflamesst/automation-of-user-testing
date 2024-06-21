from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker
from typing import List

engine = create_async_engine('sqlite+aiosqlite:///db.sqlite3', echo=True)

async_session=async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id=mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(40), nullable=True)
    group: Mapped[str] = mapped_column(String(10), nullable=True)
    age: Mapped[int] = mapped_column(nullable=True)
    username: Mapped[str] = mapped_column(String(30), nullable=True)
    count_true_answers: Mapped[int] = mapped_column(default=0)
    selected_topic: Mapped[int] = mapped_column(nullable=True)

class Topic(Base):
    __tablename__ = 'topics'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    topic_name: Mapped[str] = mapped_column(String(50))
    count_true_answers: Mapped[int] = mapped_column( )
    
class Question(Base):
    __tablename__ = 'questions'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(1024))
    topic: Mapped[int] = mapped_column(ForeignKey('topics.id'))
    true: Mapped[str] = mapped_column(String(5))
    count: Mapped[int] = mapped_column(nullable=True)

class Result(Base):
    __tablename__ = 'results'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[BigInteger] = mapped_column(BigInteger)
    topic: Mapped[int] = mapped_column(ForeignKey('topics.id'), nullable=True)
    result: Mapped[int] = mapped_column(default=0, nullable=True)

class Answer(Base):
    __tablename__ = 'answers'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey('topics.id'))
    question_id: Mapped[int] = mapped_column(ForeignKey('questions.id'))
    answer: Mapped[str] = mapped_column(String(1024), nullable=True)


class Description(Base):
    __tablename__ = 'descriptions'

    id: Mapped[int] = mapped_column(primary_key=True)
    min_value: Mapped[int] = mapped_column()
    max_value: Mapped[int] = mapped_column()
    topic_id: Mapped[int] = mapped_column(ForeignKey('topics.id'))
    description: Mapped[str] = mapped_column(String(1024), nullable=True)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)