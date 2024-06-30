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
    questions_count: Mapped[int] = mapped_column(nullable=True)
    
class Question(Base):
    __tablename__ = 'questions'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(1024))
    topic: Mapped[int] = mapped_column(ForeignKey('topics.id'))
    true: Mapped[str] = mapped_column(String(5), nullable=True)
    type: Mapped[str] = mapped_column(String(20), nullable=True)
    is_reverse: Mapped[bool] = mapped_column(default=False)
    quality: Mapped[int]=mapped_column(ForeignKey('qualities.id'), nullable=True)

class Result(Base):
    __tablename__ = 'results'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[BigInteger] = mapped_column(BigInteger)
    topic: Mapped[int] = mapped_column(ForeignKey('topics.id'))
    result: Mapped[int] = mapped_column(default=0)
    
class Result_by_category(Base):
    __tablename__ = 'results_by_category'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[BigInteger] = mapped_column(BigInteger)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'), nullable=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey('topics.id'), nullable=True)
    result: Mapped[int] = mapped_column(default=0, nullable=True)
    
class Result_by_quality(Base):
    __tablename__ = 'results_by_quality'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[BigInteger] = mapped_column(BigInteger)
    quality_id: Mapped[int] = mapped_column(ForeignKey('qualities.id'), nullable=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey('topics.id'), nullable=True)
    result: Mapped[int] = mapped_column(default=0, nullable=True)

class Answer(Base):
    __tablename__ = 'answers'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey('questions.id'))
    answer_text: Mapped[str] = mapped_column(String(1024), nullable=True)
    answer: Mapped[str] = mapped_column(String(5), nullable=True)
    category: Mapped[int]=mapped_column(ForeignKey('categories.id'), nullable=True)

class Description(Base):
    __tablename__ = 'descriptions'

    id: Mapped[int] = mapped_column(primary_key=True)
    min_value: Mapped[int] = mapped_column()
    max_value: Mapped[int] = mapped_column()
    topic_id: Mapped[int] = mapped_column(ForeignKey('topics.id'))
    description: Mapped[str] = mapped_column(String(1024), nullable=True)

class Category(Base):
    __tablename__ = 'categories'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey('topics.id'))
    description: Mapped[str] = mapped_column(String(20), nullable=True)
    
class Quality(Base):
    __tablename__ = 'qualities'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey('topics.id'))
    description: Mapped[str] = mapped_column(String(100), nullable=True)
    
class Description_of_Quality(Base):
    __tablename__ = 'description_of_qualities'

    id: Mapped[int] = mapped_column(primary_key=True)
    min_value: Mapped[int] = mapped_column()
    max_value: Mapped[int] = mapped_column()
    quality_id: Mapped[int] = mapped_column(ForeignKey('qualities.id'), nullable=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey('topics.id'))
    description: Mapped[str] = mapped_column(String(1024), nullable=True)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)