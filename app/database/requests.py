from app.database.models import async_session
from app.database.models import User, Topic, Question, Answer, Category, Quality, Role, TopicAccess
from app.database.models import Description, Description_of_Quality
from app.database.models import Result, Result_by_category, Result_by_quality
from sqlalchemy import select, update, insert, delete
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

async def add_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()
            return False
        return True 
    
async def edit_user(tg_id, name: str, group: str | None, age: int, username: str | None = None,
                    city: str | None = None, univercity: str | None = None, institute: str | None = None, 
                    department: str | None = None, stream: str | None = None, role: Role = Role.STUDENT) -> None:
    async with async_session() as session:
        update_values = {}
        if name is not None: update_values['name'] = name
        if group is not None: update_values['group'] = None if group == "-" else group
        if age is not None: update_values['age'] = age
        if username is not None: update_values['username'] = None if username == "-" else username
        if city is not None: update_values['city'] = None if city == "-" else city
        if univercity is not None: update_values['univercity'] = None if univercity == "-" else univercity
        if institute is not None: update_values['institute'] = None if institute == "-" else institute
        if department is not None: update_values['department'] = None if department == "-" else department
        if stream is not None: update_values['stream'] = None if stream == "-" else stream
        if role is not None: update_values['role'] = role
        
        await session.execute(update(User).where(User.tg_id == tg_id).values(**update_values))
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
    
async def get_all_topics():
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
        
async def add_topic(topic_name: str, questions_count: int, creator_id) -> Topic:
    async with async_session() as session:
        new_topic = Topic(topic_name=topic_name,
                          questions_count=questions_count,
                          topic_creator=creator_id)
        session.add(new_topic)
        await session.commit()
        await session.refresh(new_topic)
        return new_topic

async def add_topic_access(topic_id: int, access_type: str, access_value: str) -> TopicAccess:
    async with async_session() as session:
        existing_rule = await session.scalar(
            select(TopicAccess).where(
                TopicAccess.topic_id == topic_id,
                TopicAccess.access_type == access_type,
                TopicAccess.access_value == access_value
            )
        )
        if existing_rule:
            return existing_rule
            
        new_access = TopicAccess(topic_id=topic_id, access_type=access_type, access_value=access_value)
        session.add(new_access)
        await session.commit()
        await session.refresh(new_access)
        return new_access

async def get_topic_access_rules(topic_id: int) -> list[TopicAccess]:
    async with async_session() as session:
        result = await session.execute(select(TopicAccess).where(TopicAccess.topic_id == topic_id))
        return result.scalars().all()

async def get_topics_by_creator(creator_tg_id) -> list[Topic]:
    async with async_session() as session:
        result = await session.execute(select(Topic).where(Topic.topic_creator == creator_tg_id))
        return result.scalars().all()

async def get_topics_for_user(user_data: User) -> list[Topic]:
    async with async_session() as session:
        all_topics = (await session.execute(select(Topic))).scalars().all()

        accessible_topics = []
        for topic in all_topics:
            access_rules = await get_topic_access_rules(topic.id)

            is_accessible = False
            if not access_rules:
                pass 
            else:
                for rule in access_rules:
                    if rule.access_type == 'open_to_all':
                        is_accessible = True
                        break
                    elif rule.access_type == 'group' and user_data.group and \
                         user_data.group.lower() == rule.access_value.lower():
                        is_accessible = True
                        break
                    elif rule.access_type == 'stream' and user_data.stream and \
                         user_data.stream.lower() == rule.access_value.lower():
                        is_accessible = True
                        break
                    elif rule.access_type == 'department' and user_data.department and \
                         user_data.department.lower() == rule.access_value.lower():
                        is_accessible = True
                        break
                    elif rule.access_type == 'institute' and user_data.institute and \
                         user_data.institute.lower() == rule.access_value.lower():
                        is_accessible = True
                        break
            
            if is_accessible:
                accessible_topics.append(topic)
        return accessible_topics

async def add_category(topic_id: int, description: str) -> Category:
    async with async_session() as session:
        category = Category(topic_id=topic_id, description=description)
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category

async def add_quality(topic_id: int, description: str) -> Quality:
    async with async_session() as session:
        quality = Quality(topic_id=topic_id, description=description)
        session.add(quality)
        await session.commit()
        await session.refresh(quality)
        return quality

async def add_description_range(topic_id: int, min_val: int, max_val: int, description_text: str) -> Description:
    async with async_session() as session:
        new_desc = Description(min_value=min_val, max_value=max_val,
                               topic_id=topic_id, description=description_text)
        session.add(new_desc)
        await session.commit()
        await session.refresh(new_desc)
        return new_desc

async def add_quality_description_range(topic_id: int, quality_id: int, min_val: int, max_val: int, description_text: str) -> Description_of_Quality:
    async with async_session() as session:
        new_desc = Description_of_Quality(min_value=min_val, max_value=max_val,
                                          quality_id=quality_id, topic_id=topic_id,
                                          description=description_text)
        session.add(new_desc)
        await session.commit()
        await session.refresh(new_desc)
        return new_desc

async def add_question(topic_id: int, text: str, q_type: str, true_answer: str | None = None, is_reverse: bool = False, quality_id: int | None = None) -> Question:
    async with async_session() as session:
        new_question = Question(topic=topic_id, text=text, type=q_type,
                                true=true_answer, is_reverse=is_reverse, quality=quality_id)
        session.add(new_question)
        await session.commit()
        await session.refresh(new_question)
        return new_question

async def add_answer(question_id: int, answer_text: str, answer_value: str | None = None, category_id: int | None = None) -> Answer:
    async with async_session() as session:
        new_answer = Answer(question_id=question_id, answer_text=answer_text,
                            answer=answer_value, category=category_id)
        session.add(new_answer)
        await session.commit()
        await session.refresh(new_answer)
        return new_answer
    
async def update_question_text(question_id: int, new_text: str) -> None:
    async with async_session() as session:
        await session.execute(update(Question).where(Question.id == question_id).values(text=new_text))
        await session.commit()
        
async def update_question_true_answer(question_id: int, new_true_answer: str | None) -> None:
    async with async_session() as session:
        answer_to_save = new_true_answer if new_true_answer else None
        await session.execute(update(Question).where(Question.id == question_id).values(true=answer_to_save))
        await session.commit()

async def get_answer(answer_id: int):
    async with async_session() as session:
        return await session.scalar(select(Answer).where(Answer.id == answer_id))

async def update_answer_text(answer_id: int, new_text: str) -> None:
    async with async_session() as session:
        await session.execute(update(Answer).where(Answer.id == answer_id).values(answer_text=new_text))
        await session.commit()

async def update_answer_value(answer_id: int, new_value: str) -> None:
    async with async_session() as session:
        await session.execute(update(Answer).where(Answer.id == answer_id).values(answer=new_value))
        await session.commit()

async def update_answer_category(answer_id: int, new_category_id: int | None) -> None:
    async with async_session() as session:
        await session.execute(update(Answer).where(Answer.id == answer_id).values(category=new_category_id))
        await session.commit()

async def delete_answer(answer_id: int) -> bool:
    async with async_session() as session:
        try:
            result = await session.execute(delete(Answer).where(Answer.id == answer_id))
            await session.commit()
            return result.rowcount > 0
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при удалении ответа {answer_id}: {e}")
            return False

async def delete_topic_and_all_related_data(topic_id: int) -> bool:
    async with async_session() as session:
        try:
            questions_to_delete = (await session.scalars(select(Question).where(Question.topic == topic_id))).all()
            question_ids = [q.id for q in questions_to_delete]

            if question_ids:
                await session.execute(delete(Answer).where(Answer.question_id.in_(question_ids)))

            await session.execute(delete(Question).where(Question.topic == topic_id))

            await session.execute(delete(TopicAccess).where(TopicAccess.topic_id == topic_id))

            await session.execute(delete(Description).where(Description.topic_id == topic_id))

            await session.execute(delete(Description_of_Quality).where(Description_of_Quality.topic_id == topic_id))

            await session.execute(delete(Result).where(Result.topic == topic_id))
            await session.execute(delete(Result_by_category).where(Result_by_category.topic_id == topic_id))
            await session.execute(delete(Result_by_quality).where(Result_by_quality.topic_id == topic_id))

            await session.execute(delete(Category).where(Category.topic_id == topic_id))

            await session.execute(delete(Quality).where(Quality.topic_id == topic_id))

            await session.execute(delete(Topic).where(Topic.id == topic_id))

            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при удалении темы {topic_id}: {e}")
            return False