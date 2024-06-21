from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.requests import get_topics, get_questions, get_users

def create_callback_data(action, question_id, answer):
    return f"{action}:{question_id}:{answer}"

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

async def answering(question_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Да", 
                                      callback_data=create_callback_data('answer', question_id, 'Yes')))
    keyboard.add(InlineKeyboardButton(text="Нет", 
                                      callback_data=create_callback_data('answer', question_id, 'No')))
    return keyboard.adjust(2).as_markup()