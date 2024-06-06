from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.requests import get_topics, get_questions

async def all_topics():
    topics = await get_topics()
    keyboard = InlineKeyboardBuilder()
    for topic in topics:
        keyboard.add(InlineKeyboardButton(text=topic.topic_name, callback_data=f"topic_{topic.id}"))
    return keyboard.adjust(1).as_markup()

async def answer():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Да', callback_data="Yes"))
    keyboard.add(InlineKeyboardButton(text='Нет', callback_data="No"))
    return keyboard.adjust(2).as_markup()
    