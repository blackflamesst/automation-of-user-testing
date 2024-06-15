from app.database.models import async_session
from app.database.models import User, Topic, Question, Result, Answer
from sqlalchemy import select, update, delete

async def add_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()
            return False
        elif user.username:
            return True
        return False
    
async def edit_user(tg_id, name, group, age, username=None):
    async with async_session() as session:
        user = await session.execute(update(User).where(User.tg_id == tg_id).values(name=name,
                                                                                   group=group,
                                                                                   age=age,
                                                                                   username=username))
        await session.commit()

async def edit_user_topic(tg_id, topic_id):
    async with async_session() as session:
        user = await session.execute(update(User).where(User.tg_id == tg_id).values(selected_topic=topic_id))
        await session.commit()

async def edit_result(user_id, topic_id, result):
    async with async_session() as session:
        user = await session.execute(update(Result).where(Result.user == user_id).values(topic = topic_id, result=result))
        await session.commit()
        
async def get_topics():
    async with async_session() as session:
        return await session.scalars(select(Topic))
    
async def get_topic(topic_id):
    async with async_session() as session:
        return await session.scalar(select(Topic).where(Topic.id == topic_id))
        
async def get_questions(topic_id):
    async with async_session() as session:
        result = await session.execute(select(Question).where(Question.topic == topic_id))
        return result.scalars().all()
        
async def get_question(question_id):
    async with async_session() as session:
        return await session.scalar(select(Question).where(Question.id == question_id))
    
async def get_next_question(theme_id, current_question_id):
    async with async_session() as session:
        return await session.scalar(
            select(Question).where(Question.topic == theme_id, 
                                   Question.id > current_question_id).order_by(Question.id.asc()))
    
async def get_answers(current_question_id):
    async with async_session() as session:
        return await session.scalars(select(Answer).where(Answer.question_id == current_question_id))