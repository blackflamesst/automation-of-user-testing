from app.database.models import async_session
from app.database.models import User, Topic, Question, Answer, Category, Quality
from app.database.models import Description, Description_of_Quality
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

async def clear_and_create_category_results(tg_id, theme, categories):
    async with async_session() as session:
        for category in categories:
            existing_result = await session.scalar(
                select(Result_by_category).where(
                    Result_by_category.user == tg_id,
                    Result_by_category.category_id == category.id,
                    Result_by_category.topic_id == theme))
            if existing_result:
                await session.execute(
                    update(Result_by_category).where(
                        Result_by_category.user == tg_id,
                        Result_by_category.category_id == category.id,
                        Result_by_category.topic_id == theme).values(result=0))
            else:
                session.add(Result_by_category(user=tg_id, category_id=category.id, topic_id=theme, result=0))   
        await session.commit()

async def clear_and_create_quality_results(tg_id, theme, qualities):
    async with async_session() as session:
        for quality in qualities:
            existing_result = await session.scalar(
                select(Result_by_quality).where(
                    Result_by_quality.user == tg_id,
                    Result_by_quality.quality_id == quality.id,
                    Result_by_quality.topic_id == theme))
            if existing_result:
                await session.execute(
                    update(Result_by_quality).where(
                        Result_by_quality.user == tg_id,
                        Result_by_quality.quality_id == quality.id,
                        Result_by_quality.topic_id == theme).values(result=0))
            else:
                session.add(Result_by_quality(user=tg_id, quality_id=quality.id, topic_id=theme, result=0))   
        await session.commit()

async def edit_result_by_category(tg_id, category_id, topic, answer=1):
    async with async_session() as session:
        await session.execute(update(Result_by_category).where(Result_by_category.user == tg_id,
                        Result_by_category.category_id==category_id, 
                        Result_by_category.topic_id==topic).values(result=Result_by_category.result + answer))
        await session.commit()
    
async def edit_result_by_quality(tg_id, quality_id, topic, answer=1):
    async with async_session() as session:
        await session.execute(update(Result_by_quality).where(Result_by_quality.user == tg_id, 
                        Result_by_quality.topic_id==topic,
                        Result_by_quality.quality_id==quality_id).values(result=Result_by_quality.result + answer))
        await session.commit()

async def clear_topic_result(tg_id):
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == tg_id).values(selected_topic=0,
                                                                             count_true_answers = 0))
        await session.commit()

async def get_categories(topic):
    async with async_session() as session:
        result = await session.execute(select(Category).where(Category.topic_id == topic))
        return result.scalars().all()
    
async def get_category(category_id):
    async with async_session() as session:
        return await session.scalar(select(Category).where(Category.id == category_id))

async def get_qualities(topic):
    async with async_session() as session:
        result = await session.execute(select(Quality).where(Quality.topic_id == topic))
        return result.scalars().all()
    
async def get_quality(quality_id):
    async with async_session() as session:
        return await session.scalar(select(Quality).where(Quality.id == quality_id))

async def edit_result_on_user(tg_id, answer = 1):
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == tg_id).values(count_true_answers=User.count_true_answers + answer))
        await session.commit()

async def get_user(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))

async def get_users():
    async with async_session() as session:
        return await session.scalars(select(User))

async def get_results():
    async with async_session() as session:
        return await session.scalars(select(Result))

async def get_results_from_user(user_id, topic_id):
    async with async_session() as session:
        return await session.scalars(select(Result).where(Result.user == user_id,
                                                          Result.topic == topic_id))
    
async def get_result_from_user(user_id, topic_id):
    async with async_session() as session:
        return await session.scalar(select(Result).where(Result.user == user_id,
                                                          Result.topic == topic_id))
    
async def get_results_from_user_by_categories(user_id, topic_id):
    async with async_session() as session:
        result = await session.execute(select(Result_by_category).where(Result_by_category.user == user_id,
                                                                      Result_by_category.topic_id == topic_id))
        return result.scalars().all()
    
async def get_results_from_user_by_qualities(user_id, topic_id):
    async with async_session() as session:
        result = await session.execute(select(Result_by_quality).where(Result_by_quality.user == user_id,
                                                                     Result_by_quality.topic_id == topic_id))
        return result.scalars().all()
    
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
    
async def get_description_from_quality(result, quality_id, topic_id):
    async with async_session() as session:
        return await session.scalar(select(Description_of_Quality).where(Description_of_Quality.min_value <= result,
                                                               Description_of_Quality.max_value >= result,
                                                               Description_of_Quality.topic_id == topic_id,
                                                               Description_of_Quality.quality_id == quality_id))