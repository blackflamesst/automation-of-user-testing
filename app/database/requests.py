from app.database.models import async_session
from app.database.models import User, Topic, Question, Answer, Category, Quality
from app.database.models import Description, Description_of_Category, Description_of_Quality
from app.database.models import Result, Result_by_category, Result_by_quality
from sqlalchemy import select, update

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
        await session.execute(update(User).where(User.tg_id == tg_id).values(name=name,
                                                                            group=group,
                                                                            age=age,
                                                                            username=username))
        await session.commit()

async def edit_user_topic(tg_id, topic_id):
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == tg_id).values(selected_topic=topic_id))
        await session.commit()

async def add_result(tg_id, topic_id, user_result):
    async with async_session() as session:
        result = await session.scalar(select(Result).where(Result.user == tg_id, Result.topic==topic_id))
        if not result:
            session.add(Result(user=tg_id, topic=topic_id))
        await session.execute(update(Result).where(Result.user == tg_id, 
                                                   Result.topic==topic_id).values(result=user_result))
        await session.commit()
        
async def add_result_by_category(tg_id, category_id, topic_id):
    async with async_session() as session:
        result = await session.scalar(select(Result_by_category).where(Result_by_category.user == tg_id, 
                                                                       Result_by_category.topic_id==topic_id,
                                                                       Result_by_category.category_id==category_id))
        if not result:
            session.add(Result(user=tg_id, topic=topic_id))
        await session.execute(update(Result_by_category).where(Result_by_category.user == tg_id,
                                                               Result_by_category.category_id==category_id, 
                                                               Result_by_category.topic_id==topic_id).values(result=Result_by_category.result + 1))
        await session.commit()
        
async def add_result_by_quality(tg_id, quality_id, topic_id):
    async with async_session() as session:
        result = await session.scalar(select(Result_by_quality).where(Result_by_quality.user == tg_id, 
                                                                      Result_by_quality.topic_id==topic_id,
                                                                      Result_by_quality.quality_id==quality_id))
        if not result:
            session.add(Result(user=tg_id, topic=topic_id))
        await session.execute(update(Result_by_quality).where(Result_by_quality.user == tg_id, 
                                                              Result_by_quality.topic_id==topic_id,
                                                              Result_by_quality.quality_id==quality_id).values(result=Result_by_quality.result + 1))
        await session.commit()

async def clear_topic_result(tg_id):
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == tg_id).values(selected_topic=0,
                                                                             count_true_answers = 0))
        await session.commit()

async def edit_result_on_user(tg_id):
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == tg_id).values(count_true_answers=User.count_true_answers + 1))
        await session.commit()

async def get_last_result_from_user(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))

async def get_users():
    async with async_session() as session:
        return await session.scalars(select(User))

async def get_results():
    async with async_session() as session:
        return await session.scalars(select(Result))

async def get_results_from_user(user_id):
    async with async_session() as session:
        return await session.scalars(select(Result).where(Result.user == user_id))

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
    
async def get_description(result, topic_id):
    async with async_session() as session:
        return await session.scalar(select(Description).where(Description.min_value <= result,
                                                               Description.max_value >= result,
                                                               Description.topic_id == topic_id))