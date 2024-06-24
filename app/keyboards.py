from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.requests import get_topics, get_questions, get_users, get_answers

async def create_callback_data(action, question_id, answer, category=None, quality=None):
    return f"{action}:{question_id}:{answer}:{category}:{quality}"

async def all_topics():
    topics = await get_topics()
    keyboard = InlineKeyboardBuilder()
    for topic in topics:
        keyboard.add(InlineKeyboardButton(text=topic.topic_name, callback_data=f"topic_{topic.id}"))
    return keyboard.adjust(1).as_markup()

async def all_users():
    users = await get_users()
    keyboard = InlineKeyboardBuilder()
    for user in users:
        keyboard.add(InlineKeyboardButton(text=f'{user.name}, {user.group}', callback_data=f"user_{user.tg_id}"))
    return keyboard.adjust(1).as_markup()

async def answering(question_id, question_type):
    keyboard = InlineKeyboardBuilder()
    if question_type == 'yes_no':
        keyboard.add(InlineKeyboardButton(text="Да", callback_data=await create_callback_data('answer', question_id, 'Yes')))
        keyboard.add(InlineKeyboardButton(text="Нет", callback_data=await create_callback_data('answer', question_id, 'No')))
    elif question_type == 'variant':
        answers = await get_answers(question_id)
        for answer in answers:
            keyboard.add(InlineKeyboardButton(text=answer.answer_text, 
                                              callback_data=await create_callback_data('answer', question_id, answer.answer, answer.category, answer.quality)))
    else:
        variants = int(question_type)
        for variant in range(1, variants):
            keyboard.add(InlineKeyboardButton(text=str(variant), callback_data=await create_callback_data('answer', question_id, str(variant))))
    return keyboard.adjust(2).as_markup()